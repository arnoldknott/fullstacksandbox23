import { redirect } from '@sveltejs/kit';

import { getRequestEvent } from '$app/server';
import { IdentityProvider } from '$lib/identityProvider';

export interface OAuthProvider {
	getAccessToken(sessionId: string, scopes?: string[]): Promise<string>;
}

export type OAuthIntent = 'login' | 'reauthentication' | 'link';

export type OAuthTransaction = {
	state: string;
	intent: OAuthIntent;
	expiresAt: number;
	redirectUri: string;
	targetUrl: string;
	parentUrl?: string;
	initiatingProvider?: IdentityProvider;
	initiatingUserId?: string;
};

export function createOAuthTransaction(
	state: string,
	intent: OAuthIntent,
	timeoutSeconds: number,
	routing: Pick<OAuthTransaction, 'redirectUri' | 'targetUrl'> &
		Partial<Pick<OAuthTransaction, 'parentUrl' | 'initiatingProvider' | 'initiatingUserId'>>,
	now: number = Date.now()
): OAuthTransaction {
	return { ...routing, state, intent, expiresAt: now + timeoutSeconds * 1000 };
}

export function validateOAuthTransaction<T extends OAuthTransaction>(
	transaction: T,
	expectedState: string,
	now: number = Date.now()
): T {
	if (transaction.state !== expectedState) throw new Error('OAuth transaction state mismatch.');
	if (!['login', 'reauthentication', 'link'].includes(transaction.intent)) {
		throw new Error('OAuth transaction intent is invalid.');
	}
	if (!Number.isFinite(transaction.expiresAt) || transaction.expiresAt <= now) {
		throw new Error('OAuth transaction expired.');
	}
	return transaction;
}

export function validateOAuthIntent(intent: OAuthIntent, loggedIn: boolean): void {
	if (intent === 'login' ? loggedIn : !loggedIn) {
		throw new Error('OAuth transaction does not match the current session.');
	}
}

/** Redirect through the hidden provider resolver while preserving the current page. */
export function redirectToReauthentication(
	provider: IdentityProvider = IdentityProvider.MICROSOFT
): never {
	let targetUrl = '/';
	try {
		targetUrl = getRequestEvent().url.href;
	} catch {
		// Request context is unavailable in isolated unit tests.
	}
	redirect(307, `/login/${provider}?target-url=${encodeURIComponent(targetUrl)}`);
}
