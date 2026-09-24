import { redirect } from '@sveltejs/kit';

import { getRequestEvent } from '$app/server';
import { IdentityProvider } from '$lib/identityProvider';

export interface OAuthProvider {
	getAccessToken(sessionId: string, scopes?: string[]): Promise<string>;
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
