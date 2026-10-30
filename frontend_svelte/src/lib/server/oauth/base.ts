import { error, redirect } from '@sveltejs/kit';

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
export class OAuthTransactionUnavailableError extends Error {
	constructor(
		message: string,
		public readonly transaction?: Pick<OAuthTransaction, 'intent' | 'targetUrl' | 'parentUrl'>
	) {
		super(message);
	}
}

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
		throw new OAuthTransactionUnavailableError('OAuth transaction expired.', transaction);
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
	let event: ReturnType<typeof getRequestEvent> | undefined;
	try {
		event = getRequestEvent();
		targetUrl = event.url.href;
	} catch {
		// Request context is unavailable in isolated unit tests.
	}
	// Fetching a login page cannot complete browser authentication and may overwrite
	// the active OAuth transaction. Let the client recover from its current URL.
	if (
		event &&
		!event.isDataRequest &&
		event.request.headers.get('x-sveltekit-action') !== 'true' &&
		!event.request.headers.get('accept')?.includes('text/html')
	) {
		error(401, 'Reauthentication required');
	}
	redirect(307, `/login/${provider}?target-url=${encodeURIComponent(targetUrl)}`);
}
