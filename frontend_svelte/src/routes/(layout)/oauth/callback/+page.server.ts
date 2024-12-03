import { msalAuthProvider } from '$lib/server/oauth';
import type { PageServerLoad } from './$types';
// import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';
import AppConfig from '$lib/server/config';
// import type { AuthenticationResult } from '@azure/msal-node';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ url, cookies }) => {
	// const userAgent = request.headers.get('user-agent');
	// const referer = request.headers.get('referer');
	// const connection = request.headers.get('connection');
	// const state = url.searchParams.get('state');
	// console.log('Callback - server - load - url - search-params - state');
	// console.log(state);
	// const { targetUrl } = JSON.parse(Buffer.from(state, "base64").toString("utf8"));
	// console.log('Callback - server - load - targetUrl');
	// console.log(targetUrl);
	let targetUrl = '/';
	try {
		// Acquire tokens with the code from Microsoft Identity Platform
		// let authenticationResult: AuthenticationResult

		/******* Used previously: */

		// console.log('Callback - server - load - params');
		// console.log(params);
		// console.log('Callback - server - load - url');
		// console.log(url);
		// console.log('Callback - server - load - request');
		// console.log(request);

		// let sessionId: string | undefined;
		// try {
		const code = url.searchParams.get('code');
		// const sessionId = 'session:abc123'
		// sessionId = locals.sessionData.sessionId;
		const sessionId = cookies.get('session_id');
		const state = url.searchParams.get('state');
		if (sessionId) {
			if (state) {
				targetUrl = await msalAuthProvider.decodeState(sessionId, state);
			}
			// sessionId = `session:${cookies.get('session_id_new')}`;
			// sessionId = `session:${sessionId}`;
			await msalAuthProvider.authenticateWithCode(sessionId, code, url.origin);
			cookies.set('session_id', sessionId, {
				path: '/',
				...appConfig.session_cookie_options
			});
		} else {
			// redirect(302, '/login');
			// console.error('===> Callback - server - authenticate with Code failed - redirecting to "/" <===');
			console.error('🔥 🚪 oauth - callback - server - redirect failed');
			redirect(302, '/');
		}
	} catch (err) {
		console.error('oauth - callback - server - authenticateWithCode failed');
		console.error(err);
		throw err;
	}

	// Create a session, store authenticationResult in the cache, set the session cookie, and write to user store
	// try {
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

	// await redisCache.updateSessionExpiry(sessionId);

	// const session = await redisCache.getSession(sessionId);
	// console.log('Callback - server - session');
	// console.log(session);
	// await redisCache.setSession(sessionId, '.', session);
	// TBD: remove user_store and use locals on server side and cookies on client side instead.

	// user_store.set(session);
	// } else {
	// 	console.error('Callback - server - Account not found');
	// 	throw new error(404, 'No account found');
	// }

	// httpOnly and secure are true by default from sveltekit (https://kit.svelte.dev/docs/types#public-types-cookies)
	// secure is disabled for localhost, but enabled for all other domains
	// TBD: add expiry!
	// cookies.set('session_id', sessionId, { path: '/', httpOnly: true, sameSite: false }); //sameSite: 'strict' });
	// } catch (err) {
	// 	console.error('Callback - server - create session failed');
	// 	console.error(err);
	// 	throw err;
	// }
	// } catch (err) {
	// 	console.error('Callback session initialization failed');
	// 	console.log(err);
	// 	throw err;
	// }
	// console.log('===> Callback - server - redirecting to "/" <===');
	// redirect(302, "/");
	redirect(302, targetUrl);
};
