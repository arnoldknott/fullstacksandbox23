import { IdentityProvider } from '$lib/identityProvider';
import type { Session } from '$lib/types';

import { backendAPI } from '../apis/backendApi';
import { redisCache } from '../cache';
import AppConfig from '../config';
import type { OAuthTransaction } from './base';
import { linkedinAuthProvider } from './linkedin';
import { msalAuthProvider } from './microsoft';

const appConfig = await AppConfig.getInstance();

export type AccountMergePreview = {
	result: 'merge-required';
	preview_hash: string;
	settings: Record<string, { survivor: unknown; source: unknown }>;
	defaults: Record<string, 'survivor' | 'source'>;
};

export type AccountMergeState = AccountMergePreview & {
	linkedProvider: IdentityProvider;
	targetUrl: string;
	expiresAt: number;
};

type AccountLinkTransaction = Pick<
	OAuthTransaction,
	'targetUrl' | 'initiatingProvider' | 'initiatingUserId'
>;

export async function providerProofToken(
	sessionId: string,
	provider: IdentityProvider
): Promise<string> {
	return provider === IdentityProvider.MICROSOFT
		? msalAuthProvider.getAccessToken(sessionId)
		: linkedinAuthProvider.getIdentityToken(sessionId);
}

export async function completeAccountLink(
	sessionId: string,
	transaction: AccountLinkTransaction,
	linkedProvider: IdentityProvider
): Promise<'linked' | 'merge-required'> {
	const session = await redisCache.getSession<Session>(sessionId);
	if (
		!session?.loggedIn ||
		!transaction.initiatingProvider ||
		transaction.initiatingProvider !== session.identityProvider ||
		transaction.initiatingUserId !== session.currentUser?.id ||
		linkedProvider === session.identityProvider
	) {
		throw new Error('Account link transaction no longer matches the initiating session.');
	}
	const linkedToken = await providerProofToken(sessionId, linkedProvider);
	const response = await backendAPI.post(
		sessionId,
		'/user/me/link/preview',
		'{}',
		undefined,
		{},
		{
			'X-Account-Link-Authorization': `Bearer ${linkedToken}`
		}
	);
	if (!response.ok) throw new Error(`Account link failed with status ${response.status}.`);
	const result = (await response.json()) as
		{ result: 'linked' | 'already-linked' } | AccountMergePreview;
	if (result.result === 'merge-required') {
		const mergeState: AccountMergeState = {
			...result,
			linkedProvider,
			targetUrl: transaction.targetUrl,
			expiresAt: Date.now() + appConfig.authentication_timeout * 1000
		};
		await redisCache.setSession(sessionId, '$.accountMerge', JSON.stringify(mergeState));
		return 'merge-required';
	}
	const responseMe = await backendAPI.get(sessionId, '/user/me');
	if (!responseMe.ok) throw new Error('Linked account could not be reloaded.');
	await redisCache.setSession(sessionId, '$.currentUser', JSON.stringify(await responseMe.json()));
	return 'linked';
}
