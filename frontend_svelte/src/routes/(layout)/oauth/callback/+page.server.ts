import { msalAuthProvider } from '$lib/server/oauth';
import { redisCache } from '$lib/server/cache';
import type { PageServerLoad } from './$types';
// import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';
// import type { AuthenticationResult } from '@azure/msal-node';
import { user_store } from '$lib/stores';

export const load: PageServerLoad = async ({ url, cookies }) => {
	// const userAgent = request.headers.get('user-agent');
	// const referer = request.headers.get('referer');
	// const connection = request.headers.get('connection');
	try {
		// Acquire tokens with the code from Microsoft Identity Platform
		// let authenticationResult: AuthenticationResult;
		let sessionId: string | undefined;
		try {
			const code = url.searchParams.get('code');
			// const sessionId = 'session:abc123'
			sessionId = cookies.get('session_id');
			// sessionId = `session:${cookies.get('session_id_new')}`;
			// sessionId = `session:${sessionId}`;
			if (sessionId) {
				// authenticationResult = await msalAuthProvider.authenticateWithCode(
				await msalAuthProvider.authenticateWithCode(sessionId, code, url.origin);
			} else {
				// redirect(302, '/login');
				redirect(302, '/');
			}
		} catch (err) {
			console.error('Callback - server - authenticateWithCode failed');
			console.error(err);
			throw err;
		}

		// Create a session, store authenticationResult in the cache, set the session cookie, and write to user store
		try {
			// const sessionId = uuidv4();
			// const account = authenticationResult.account;
			// const accessToken = authenticationResult.accessToken;
			// TBD: add expiry!
			// if (account) {
			// 	// const userAgent = request.headers.get('user-agent');
			// 	const session = {
			// 		userProfile: account,
			// 		// accessToken: accessToken,
			// 		// userAgent: userAgent || '',
			// 		loggedIn: true
			// 	};
			// move to setSession in $lib/server/cache.ts:
			// const redisClient = await redisCache.provideClient();
			// await redisClient.json.set(sessionId, '$.loggedIn', true);
			await redisCache.updateSessionExpiry(sessionId);
			const session = await redisCache.getSession(sessionId);
			// console.log('Callback - server - session');
			// console.log(session);
			// await redisCache.setSession(sessionId, '.', session);
			user_store.set(session);
			// } else {
			// 	console.error('Callback - server - Account not found');
			// 	throw new Error('No account found');
			// }

			// httpOnly and secure are true by default from sveltekit (https://kit.svelte.dev/docs/types#public-types-cookies)
			// secure is disabled for localhost, but enabled for all other domains
			// TBD: add expiry!
			// cookies.set('session_id', sessionId, { path: '/', httpOnly: true, sameSite: false }); //sameSite: 'strict' });
		} catch (err) {
			console.error('Callback - server - create session failed');
			console.error(err);
			throw err;
		}
	} catch (err) {
		console.error('Callback session initialization failed');
		console.log(err);
		throw err;
	}
	redirect(302, '/');
};
