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
	try {
		const code = url.searchParams.get('code');
		const sessionId = cookies.get('session_id');
		const state = url.searchParams.get('state');
		if (sessionId) {
			// TBD CSRF protection check:
			if (state) {
				targetUrl = await msalAuthProvider.decodeState(sessionId, state);
			}
			// TBD: authenticationResult not used any more
			// but still needs to execute, as this sets the access token in cache!
			// const _authenticationResult: AuthenticationResult =
			await msalAuthProvider.authenticateWithCode(sessionId, code, url.origin);
			await redisCache.setSession(sessionId, '$.loggedIn', JSON.stringify(true));
			await redisCache.setSession(sessionId, '$.sessionId', JSON.stringify(sessionId));
			// TBD: Does the cookie really need to set again in callback? It's set already in login endpoint!
			cookies.set('session_id', sessionId, {
				path: '/',
				...appConfig.session_cookie_options
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
			if (responseMe.status === 200) {
				await redisCache.setSession(
					sessionId,
					'$.status',
					// JSON.stringify(SessionStatus.REGISTERED)
					// TBD: for devloping registration flow, set to registration pending:
					// change back to registered when registration flow is done:
					JSON.stringify(SessionStatus.REGISTRATION_PENDING)
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
	redirect(302, targetUrl);
};
