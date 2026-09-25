// import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';

// import type { AuthenticationResult } from '@azure/msal-node';
import { IdentityProvider } from '$lib/identityProvider';
import { backendAPI } from '$lib/server/apis/backendApi';
import { redisCache } from '$lib/server/cache';
import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth/microsoft';
import { SessionStatus } from '$lib/session';

import type { PageServerLoad } from './$types';

const appConfig = await AppConfig.getInstance();

function safeTarget(target: string, origin: string): string {
	const targetUrl = new URL(target, origin);
	return targetUrl.origin === origin
		? `${targetUrl.pathname}${targetUrl.search}${targetUrl.hash}`
		: '/';
}

export const load: PageServerLoad = async ({ url, cookies }) => {
	let targetUrl = '/';
	let parentUrl: string | undefined;
	let sessionId: string | undefined;
	try {
		const code = url.searchParams.get('code');
		// const sessionId = cookies.get('session_id');
		const state = url.searchParams.get('state');
		if (state) {
			[sessionId, targetUrl, parentUrl] = await msalAuthProvider.decodeState(state);
		}
		if (sessionId) {
			// TBD CSRF protection check:
			// TBD: authenticationResult not used any more
			// but still needs to execute, as this sets the access token in cache!
			// const _authenticationResult: AuthenticationResult =
			await msalAuthProvider.authenticateWithCode(sessionId, code, url.origin);
			await redisCache.setSession(sessionId, '$.sessionId', JSON.stringify(sessionId));

			const cookieOptions = appConfig.session_cookie_options as Record<string, unknown>;
			// Check if target URL is pointing to another origin - if yes, the page is embedded in an iframe
			// if (targetUrl && new URL(targetUrl).origin !== url.origin) {
			// This worked in Chrome embedded in parent-page:
			// if (parentUrl) {
			// 	cookieOptions.sameSite = 'none';
			// }
			await redisCache.setSession(
				sessionId,
				'$.identityProvider',
				JSON.stringify(IdentityProvider.MICROSOFT)
			);
			const responseMe = await backendAPI.get(sessionId, '/user/me');
			if (responseMe.status !== 200 && responseMe.status !== 201) {
				throw new Error(`Backend Microsoft signup failed with status ${responseMe.status}.`);
			}
			// TBD: consider leaving user.is_active at False after creatation and
			// show the modal dialog for updating profile and account.
			// The put -me endpoint will set is_active to True
			// No - leave as is: make the app less annoying for first time users!
			let sessionStatus: SessionStatus | undefined;
			if (responseMe.status === 200) {
				sessionStatus = SessionStatus.REGISTERED;
				// TBD: To develop the first-login registration flow with an existing user,
				// assign REGISTRATION_PENDING here. Change it back when finished:
				// sessionStatus = SessionStatus.REGISTRATION_PENDING;
			} else if (responseMe.status === 201) {
				sessionStatus = SessionStatus.REGISTRATION_PENDING;
			}
			if (sessionStatus) {
				await redisCache.setSession(sessionId, '$.status', JSON.stringify(sessionStatus));
				await redisCache.setSession(
					sessionId,
					'$.welcomePending',
					JSON.stringify(sessionStatus === SessionStatus.REGISTRATION_PENDING)
				);
			}
			const currentUser = await responseMe.json();
			await redisCache.setSession(sessionId, '$.currentUser', JSON.stringify(currentUser));
			await redisCache.setSession(sessionId, '$.loggedIn', JSON.stringify(true));
			await redisCache.updateSessionExpiry(sessionId);
			cookies.set('session_id', sessionId, {
				path: '/',
				...cookieOptions
			});
		} else {
			console.error('🔥 🚪 oauth - callback - server - redirect failed');
			redirect(302, '/');
		}
	} catch (err) {
		console.error('oauth - callback - server - authenticateWithCode failed');
		console.error(err);
		throw err;
	}
	if (parentUrl) {
		// redirect(302, parentUrl);
		// return { parentUrl: parentUrl, sessionId: sessionId };
		return { parentUrl: parentUrl };
	} else {
		redirect(302, safeTarget(targetUrl, url.origin));
	}
};
