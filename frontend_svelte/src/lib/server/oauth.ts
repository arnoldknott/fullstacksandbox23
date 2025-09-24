// import { app_config } from './config';
import AppConfig from './config';
import { redisCache } from './cache';
import type { RedisClientType } from 'redis';
import {
	ConfidentialClientApplication,
	InteractionRequiredAuthError,
	CryptoProvider,
	type AuthenticationResult
} from '@azure/msal-node';
import { building } from '$app/environment';
import {
	DistributedCachePlugin,
	type ICacheClient,
	type IPartitionManager
} from '@azure/msal-node';
import type { AccountInfo, AccountEntity } from '@azure/msal-common';
import { redirect } from '@sveltejs/kit';

const appConfig = await AppConfig.getInstance();
const scopesBackend = [
	`api://${appConfig.api_scope}/api.read`,
	`api://${appConfig.api_scope}/api.write`
];
const scopesMsGraph = [
	'User.Read',
	'openid',
	'profile',
	'offline_access',
	'Calendars.ReadWrite.Shared',
	'Files.ReadWrite.All',
	'User.ReadBasic.All',
	'Team.ReadBasic.All'
];
const scopesAzure = ['https://management.azure.com/user_impersonation']; // for onbehalfof workflow

// Note: this is only exporting the BaseOauthProvider type, not the class itself!
class BaseOauthProvider {
	constructor() {}

	async getAccessToken(_sessionId: string, _scopes: string[]): Promise<string> {
		throw new Error('Method not implemented.');
	}
}

export type { BaseOauthProvider };

class RedisClientWrapper implements ICacheClient {
	private redisClient: RedisClientType;

	constructor(redisClient: RedisClientType) {
		this.redisClient = redisClient;
	}

	public async set(key: string, value: string): Promise<string> {
		const authSessionData =
			(await this.redisClient.json.set(`msal:${key}`, '.', JSON.parse(value))) || '';

		if (authSessionData) {
			await this.redisClient.expire(`msal:${key}`, 60 * 60 * 24 * 7); // 7 days
		}
		return authSessionData;
	}

	public async get(key: string): Promise<string> {
		try {
			const authSessionData = (await this.redisClient.json.get(`msal:${key}`)) || '';
			return JSON.stringify(authSessionData);
		} catch (error) {
			console.log(error);
		}
		return '';
	}
}

// move to session from types.d.ts ?
interface SessionCacheData {
	account: AccountInfo;
	[key: string]: string | AccountInfo;
}

//
class RedisPartitionManager implements IPartitionManager {
	sessionId: string;
	redisClient: RedisClientWrapper;

	constructor(redisClient: RedisClientWrapper, sessionId: string) {
		this.sessionId = sessionId;
		this.redisClient = redisClient;
	}

	async getKey(): Promise<string> {
		try {
			const sessionData = await redisCache.getSession(this.sessionId);
			const session = sessionData as SessionCacheData;
			const account = session.microsoftAccount as AccountInfo;
			const partitionKey = account?.homeAccountId || '';
			return partitionKey;
		} catch (error) {
			console.log('Error in getKey() : ', error);
		}
		return '';
	}

	async extractKey(accountEntity: AccountEntity): Promise<string> {
		if (Object.prototype.hasOwnProperty.call(accountEntity, 'homeAccountId')) {
			return accountEntity.homeAccountId; // the homeAccountId is the partition key
		} else {
			throw new Error('homeAccountId is not found');
		}
	}
}

class MicrosoftAuthenticationProvider extends BaseOauthProvider {
	private msalCommonConfig;
	private redisClientWrapper: RedisClientWrapper;
	private cryptoProvider: CryptoProvider;

	constructor(redisClient: RedisClientType) {
		super();
		// Common configuration for all users:
		this.msalCommonConfig = {
			auth: {
				clientId: appConfig.app_reg_client_id,
				authority: appConfig.az_authority,
				clientSecret: appConfig.app_client_secret,
				scopes: [...scopesBackend, ...scopesMsGraph]
			}
		};
		this.cryptoProvider = new CryptoProvider();
		this.redisClientWrapper = new RedisClientWrapper(redisClient);
	}

	private createMsalConfClient(sessionId: string): ConfidentialClientApplication {
		try {
			// add the cachePlugin to the configuration:
			// instance of MicrosoftTokenCache with the RedisClientWrapper and RedisPartitionManager,
			// where RedisPartitionManager is initialized with the sessionId - so per user only!

			if (!building) {
				const partitionManager = new RedisPartitionManager(this.redisClientWrapper, sessionId);

				const tokenCache = new DistributedCachePlugin(this.redisClientWrapper, partitionManager);
				const msalUserSessionSpecificConfig = {
					...this.msalCommonConfig,
					cache: { cachePlugin: tokenCache }
				};
				const msalConfClient = new ConfidentialClientApplication(msalUserSessionSpecificConfig);
				return msalConfClient;
			} else {
				const msalConfClient = new ConfidentialClientApplication(this.msalCommonConfig);
				console.log(
					'👎 🔑 oauth - Authentication - MsalConfClient - created without Cache (not necessary during build stage)!'
				);
				return msalConfClient;
			}
		} catch (error) {
			console.error('🔥 🔑 oauth - Authentication - MsalConfClient - createMsalConfClient failed');
			console.log(error);
			throw new Error(
				'🔥 🔑 oauth - Authentication - MsalConfClient - createMsalConfClient failed ' + error
			);
		}
	}

	public async signIn(
		sessionId: string,
		origin: string,
		targetUrl: string = '/',
		scopes: string[] = [...scopesBackend, ...scopesMsGraph, ...scopesAzure]
	): Promise<string> {
		try {
			// console.log('🔑 oauth - Authentication - signIn ');
			const csrfToken = this.cryptoProvider.createNewGuid();
			const state = this.cryptoProvider.base64Encode(
				JSON.stringify({
					csrfToken: csrfToken,
					targetURL: targetUrl
				})
			);
			await redisCache.setSession(sessionId, '$.csrfToken', JSON.stringify(csrfToken), 60 * 10);
			const msalConfClient = this.createMsalConfClient(sessionId);
			// pass the state here as well, so user can get redirected to the correct page after login:
			// for example: https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/7a01aafc1af9aca6d51638204aa942700c0418ca/samples/msal-node-samples/auth-code-distributed-cache/src/AuthProvider.ts#L84
			const authCodeUrlParameters = {
				scopes: scopes,
				redirectUri: `${origin}/oauth/callback`,
				state: state
			};
			const authCodeUrl = await msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
			return authCodeUrl;
		} catch (error) {
			console.error('🔥 🔑 oauth - Authentication - signIn failed');
			console.error(error);
			throw error;
		}
	}

	public async decodeState(sessionId: string, state: string): Promise<string> {
		const stateJSON = JSON.parse(this.cryptoProvider.base64Decode(state));
		const cachedCsrfToken = await redisCache.getSession(sessionId, '$.csrfToken');
		if (stateJSON.csrfToken === cachedCsrfToken) {
			return stateJSON.targetURL;
		} else {
			throw new Error('CSRF Token mismatch');
		}
	}

	public async authenticateWithCode(
		sessionId: string,
		code: string | null,
		origin: string,
		scopes: string[] = scopesMsGraph
	): Promise<AuthenticationResult> {
		if (!code) {
			throw new Error('🔥 🔑 oauth - GetAccessToken failed - no code');
		}
		try {
			// console.log('🔑 oauth - Authentication - authenticateWithCode ');
			const msalConfClient = this.createMsalConfClient(sessionId);
			const response = await msalConfClient.acquireTokenByCode({
				code: code,
				scopes: scopes,
				redirectUri: `${origin}/oauth/callback`
			});
			const accountData = response.account ? JSON.parse(JSON.stringify(response.account)) : null;
			await redisCache.setSession(sessionId, '$.microsoftAccount', JSON.stringify(accountData));

			return response;
		} catch (error) {
			console.error('🔥 🔑 oauth - GetAccessToken failed');
			console.error(error);
			throw error;
		}
	}

	public async getAccessToken(
		sessionId: string,
		scopes: string[] = [appConfig.api_scope_default]
	): Promise<string> {
		try {
			// console.log('🔑 oauth - Authentication - getAccessToken ');
			const msalConfClient = this.createMsalConfClient(sessionId);
			await msalConfClient.getTokenCache().getAllAccounts(); // required for triggering beforeCacheACcess
			const account = (await redisCache.getSession(sessionId, '$.microsoftAccount')) as AccountInfo;
			const response = await msalConfClient.acquireTokenSilent({
				scopes: scopes,
				account: account
			});
			const accessToken = response.accessToken;
			return accessToken;
		} catch (error) {
			if (error instanceof InteractionRequiredAuthError) {
				console.warn('👎 🔑 oauth - GetAccessToken silent failed - sign in again!');
				redirect(307, '/login');
			} else {
				console.error('🔥 🔑 oauth - GetAccessToken failed');
				console.error(error);
				throw error;
			}
		}
	}
}

if (!redisCache) {
	throw new Error('🔑🔥 oauth - Authentication - redisCache not initialized');
}
const redisClient = !building ? await redisCache.provideClient() : ({} as RedisClientType);
export const msalAuthProvider = new MicrosoftAuthenticationProvider(redisClient);

console.log('👍 🔑 lib - server - oauth.ts - end');
