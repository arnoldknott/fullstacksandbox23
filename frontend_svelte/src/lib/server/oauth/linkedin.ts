import * as client from 'openid-client';

import { IdentityProvider } from '$lib/identityProvider';

import { redisCache } from '../cache';
import AppConfig from '../config';
import type { OAuthProvider } from './base';

type LinkedInAuthorization = {
	state: string;
	redirectUri: string;
	targetUrl: string;
	parentUrl?: string;
};

type LinkedInTokens = {
	accessToken: string;
	idToken: string;
	refreshToken?: string;
	tokenType?: string;
	scope?: string;
	accessTokenExpiresAt?: number;
	idTokenExpiresAt: number;
	subject: string;
};

const appConfig = await AppConfig.getInstance();

export class LinkedInReauthenticationRequiredError extends Error {}

class LinkedInAuthenticationProvider implements OAuthProvider {
	private configuration?: Promise<client.Configuration>;

	private getConfiguration(): Promise<client.Configuration> {
		if (!appConfig.linkedin_client_id || !appConfig.linkedin_client_secret) {
			throw new Error('LinkedIn authentication is not configured.');
		}
		// LinkedIn's 3-legged authorization-code flow requires the frontend server to
		// send its client credentials in the request body during the code exchange.
		this.configuration ??= client.discovery(
			new URL(appConfig.linkedin_issuer),
			appConfig.linkedin_client_id,
			undefined,
			client.ClientSecretPost(appConfig.linkedin_client_secret)
		);
		return this.configuration;
	}

	private callbackUrl(origin: string): string {
		return `${origin}/oauth/callback/linkedin`;
	}

	private async getAuthorization(sessionId: string): Promise<LinkedInAuthorization> {
		const value = await redisCache.getSession(sessionId, '$.linkedinAuthorization');
		if (!value || typeof value !== 'object' || !('state' in value)) {
			throw new Error('LinkedIn authorization session was not found.');
		}
		return value as LinkedInAuthorization;
	}

	private async getTokens(sessionId: string): Promise<LinkedInTokens> {
		const subject = await redisCache.getSession<string>(sessionId, '$.linkedinSubject');
		if (typeof subject !== 'string' || !subject) {
			throw new LinkedInReauthenticationRequiredError('LinkedIn session was not found.');
		}
		const redisKey = `linkedin:${subject}`;
		const redis = await redisCache.provideClient();
		const tokens = await redis?.json.get(redisKey);
		if (!tokens || typeof tokens !== 'object' || !('idToken' in tokens)) {
			throw new LinkedInReauthenticationRequiredError('LinkedIn credentials were not found.');
		}
		return tokens as LinkedInTokens;
	}

	private async saveTokens(tokens: LinkedInTokens, expiresIn?: number): Promise<void> {
		const redisKey = `linkedin:${tokens.subject}`;
		const redis = await redisCache.provideClient();
		if (!redis) throw new Error('Redis is unavailable.');
		await redis.json.set(redisKey, '$', tokens);
		await redis.expire(redisKey, Math.max(expiresIn ?? 0, appConfig.session_timeout));
	}

	private async refresh(tokens: LinkedInTokens): Promise<LinkedInTokens> {
		if (!tokens.refreshToken) {
			throw new LinkedInReauthenticationRequiredError('LinkedIn sign-in has expired.');
		}
		const response = await client.refreshTokenGrant(
			await this.getConfiguration(),
			tokens.refreshToken
		);
		const claims = response.claims();
		if (!response.id_token || !claims || claims.sub !== tokens.subject || !claims.exp) {
			throw new LinkedInReauthenticationRequiredError('LinkedIn did not renew the identity token.');
		}
		const refreshed: LinkedInTokens = {
			accessToken: response.access_token,
			idToken: response.id_token,
			refreshToken: response.refresh_token ?? tokens.refreshToken,
			tokenType: response.token_type,
			scope: response.scope,
			accessTokenExpiresAt: response.expires_in
				? Math.floor(Date.now() / 1000) + response.expires_in
				: undefined,
			idTokenExpiresAt: claims.exp,
			subject: tokens.subject
		};
		await this.saveTokens(refreshed, response.expires_in);
		return refreshed;
	}

	async signIn(
		sessionId: string,
		origin: string,
		targetUrl: string = '/',
		parentUrl?: string
	): Promise<string> {
		const configuration = await this.getConfiguration();
		const state = `${sessionId}.${client.randomState()}`;
		const redirectUri = this.callbackUrl(origin);
		const authorization: LinkedInAuthorization = {
			state,
			redirectUri,
			targetUrl,
			parentUrl
		};
		await redisCache.setSession(
			sessionId,
			'$.linkedinAuthorization',
			JSON.stringify(authorization)
		);
		return client.buildAuthorizationUrl(configuration, {
			redirect_uri: redirectUri,
			response_type: 'code',
			scope: 'openid profile',
			state
		}).href;
	}

	async authenticateWithCode(currentUrl: URL): Promise<{
		sessionId: string;
		targetUrl: string;
		parentUrl?: string;
	}> {
		const state = currentUrl.searchParams.get('state');
		const separator = state?.indexOf('.') ?? -1;
		if (!state || separator < 1) throw new Error('Invalid LinkedIn callback state.');
		const sessionId = state.slice(0, separator);
		const authorization = await this.getAuthorization(sessionId);
		if (!authorization.redirectUri) {
			throw new Error('LinkedIn authorization redirect URI was not found.');
		}
		const authorizationResponseUrl = new URL(authorization.redirectUri);
		authorizationResponseUrl.search = currentUrl.search;
		const response = await client
			.authorizationCodeGrant(await this.getConfiguration(), authorizationResponseUrl, {
				expectedState: authorization.state,
				idTokenExpected: true
			})
			.catch((error: unknown) => {
				if (error instanceof client.ResponseBodyError) {
					console.error('🔥 🔑 === LinkedIn token exchange - OAuth error ===');
					console.error({
						status: error.status,
						error: error.error,
						errorDescription: error.error_description
					});
				} else if (error instanceof client.ClientError) {
					const cause = error.cause;
					console.error('🔥 🔑 === LinkedIn identity-token validation error ===');
					console.error({
						code: error.code,
						causeCode:
							cause && typeof cause === 'object' && 'code' in cause
								? String(cause.code)
								: undefined,
						causeMessage: cause instanceof Error ? cause.message : undefined
					});
				}
				throw error;
			});
		await redisCache.deleteSessionPath(sessionId, '$.linkedinAuthorization');
		const claims = response.claims();
		if (!response.id_token || !claims?.sub || !claims.exp) {
			throw new Error('LinkedIn did not return a valid identity token.');
		}
		const tokens: LinkedInTokens = {
			accessToken: response.access_token,
			idToken: response.id_token,
			refreshToken: response.refresh_token,
			tokenType: response.token_type,
			scope: response.scope,
			accessTokenExpiresAt: response.expires_in
				? Math.floor(Date.now() / 1000) + response.expires_in
				: undefined,
			idTokenExpiresAt: claims.exp,
			subject: claims.sub
		};
		await this.saveTokens(tokens, response.expires_in);
		await redisCache.setSession(sessionId, '$.linkedinSubject', JSON.stringify(claims.sub));
		await redisCache.setSession(
			sessionId,
			'$.identityProvider',
			JSON.stringify(IdentityProvider.LINKEDIN)
		);
		return {
			sessionId,
			targetUrl: authorization.targetUrl,
			parentUrl: authorization.parentUrl
		};
	}

	async getIdentityToken(sessionId: string): Promise<string> {
		let tokens = await this.getTokens(sessionId);
		if (tokens.idTokenExpiresAt <= Math.floor(Date.now() / 1000)) {
			tokens = await this.refresh(tokens);
		}
		return tokens.idToken;
	}

	async getAccessToken(sessionId: string): Promise<string> {
		let tokens = await this.getTokens(sessionId);
		if (
			tokens.accessTokenExpiresAt !== undefined &&
			tokens.accessTokenExpiresAt <= Math.floor(Date.now() / 1000)
		) {
			tokens = await this.refresh(tokens);
		}
		return tokens.accessToken;
	}

	async assertUserInfoSubject(sessionId: string, subject: string): Promise<void> {
		const tokens = await this.getTokens(sessionId);
		if (subject !== tokens.subject) {
			throw new Error('LinkedIn UserInfo subject does not match the authenticated identity.');
		}
	}
}

export const linkedinAuthProvider = new LinkedInAuthenticationProvider();
