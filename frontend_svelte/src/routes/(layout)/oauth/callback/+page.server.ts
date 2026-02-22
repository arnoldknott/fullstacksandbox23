import { msalAuthProvider } from '$lib/server/oauth';
import type { PageServerLoad } from './$types';
// import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';
import AppConfig from '$lib/server/config';
import { redisCache } from '$lib/server/cache';
import type { User as MicrosoftProfile } from '@microsoft/microsoft-graph-types';
// import type { AuthenticationResult } from '@azure/msal-node';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import { SessionStatus } from '$lib/session';

const appConfig = await AppConfig.getInstance();

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
			await redisCache.setSession(sessionId, '$.loggedIn', JSON.stringify(true));
			await redisCache.setSession(sessionId, '$.sessionId', JSON.stringify(sessionId));

			const cookieOptions = appConfig.session_cookie_options as Record<string, unknown>;
			// Check if targetURL is pointing to another origin - if yes, the page is embedded in an iframe
			// if (targetUrl && new URL(targetUrl).origin !== url.origin) {
			// This worked in Chrome embedded in parent-page:
			// if (parentUrl) {
			// 	cookieOptions.sameSite = 'none';
			// }
			cookies.set('session_id', sessionId, {
				path: '/',
				...cookieOptions
			});
			// const response = await fetch(`${appConfig.ms_graph_base_uri}/me`, {
			// 	headers: {
			// 		Authorization: `Bearer ${authenticationResult.accessToken}`
			// 	}
			// });
			// const microsoftProfile = (await response.json()) as MicrosoftProfile;
			const responseMicrosoftProfile = await microsoftGraph.get(sessionId, '/me');
			const microsoftProfile = (await responseMicrosoftProfile.json()) as MicrosoftProfile;
			await redisCache.setSession(
				sessionId,
				'$.microsoftProfile',
				JSON.stringify(microsoftProfile)
			);
			const responseMe = await backendAPI.get(sessionId, '/user/me');
			// TBD: consider leaving user.is_active at False after creatation and
			// show the modal dialog for updating profile and account.
			// The put -me endpoint will set is_active to True
			// No - leave as is: make the app less annoying for first time users!
			if (responseMe.status === 200) {
				await redisCache.setSession(
					sessionId,
					'$.status',
					JSON.stringify(SessionStatus.REGISTERED)
					// TBD: for devloping registration flow, set to registration pending:
					// change back to registered when registration flow is done:
					// JSON.stringify(SessionStatus.REGISTRATION_PENDING)
				);
			} else if (responseMe.status === 201) {
				await redisCache.setSession(
					sessionId,
					'$.status',
					JSON.stringify(SessionStatus.REGISTRATION_PENDING)
				);
			}
			const currentUser = await responseMe.json();
			await redisCache.setSession(sessionId, '$.currentUser', JSON.stringify(currentUser));
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
		redirect(302, targetUrl);
	}
};
