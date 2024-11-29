import { msalAuthProvider } from '$lib/server/oauth';
import { redisCache } from '$lib/server/cache';
import type { PageServerLoad } from './$types';
// import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';
// import type { AuthenticationResult } from '@azure/msal-node';
import { user_store } from '$lib/stores';

export const load: PageServerLoad = async ({ url, cookies, request, params }) => {
	// const userAgent = request.headers.get('user-agent');
	// const referer = request.headers.get('referer');
	// const connection = request.headers.get('connection');
	// const state = url.searchParams.get('state');
	// console.log('Callback - server - load - url - search-params - state');
	// console.log(state);
	// const { targetUrl } = JSON.parse(Buffer.from(state, "base64").toString("utf8"));
	// console.log('Callback - server - load - targetUrl');
	// console.log(targetUrl);
	const state = url.searchParams.get('state');
	const targetUrl = await msalAuthProvider.decodeState(state);
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



		let sessionId: string | undefined;
		try {
			const code = url.searchParams.get('code');
			// const sessionId = 'session:abc123'
			sessionId = cookies.get('session_id');
			// sessionId = `session:${cookies.get('session_id_new')}`;
			// sessionId = `session:${sessionId}`;
			if (sessionId) {
				// authenticationResult = await msalAuthProvider.authenticateWithCode(
				// TBD: at this time the session is not set yet in the cache; that's what causes the errors at first login
				const authResult = await msalAuthProvider.authenticateWithCode(sessionId, code, url.origin);
				// console.log('Callback - server - authenticateWithCode - authResult');
				// console.log(authResult);
				// console.log('Callback - server - authenticateWithCode - request ');
				// console.log(request);
				// const { targetUrl } = JSON.parse(Buffer.from(request.body.state, "base64").toString("utf8"));
				// console.log('Callback - server - targetUrl');
				// console.log(targetUrl);
				// redirect(302, '/');
			} else {
				// redirect(302, '/login');
				// console.error('===> Callback - server - authenticate with Code failed - redirecting to "/" <===');
				redirect(302, '/');
			}

		/*********  */

		/***** New? */

		// try {
		// 	const code = url.searchParams.get('code');
		// 	await msalAuthProvider.authenticateWithCode(code, url.origin);
		// 	} else {
		// 		// redirect(302, '/login');
		// 		console.error('===> Callback - server - authenticate with Code failed - redirecting to "/" <===');
		// 		redirect(302, '/');
		// 	}

		// // create the session uuid here:
		// const sessionId = `session:${v4()}`;
		// const userAgent = request.headers.get('user-agent');
		// // Type that one:
		// const sessionData: Session = {
		// 	loggedIn: false,
		// 	userAgent: userAgent || ''
		// };

		// const redisClient = await redisCache.provideClient();
		// await redisClient.json.set(sessionId, '$', Object(sessionData));
		// await redisClient.expire(sessionId, 20); // use sessionTimeout from cache.ts

		// user_store.set(sessionData);

		// // cookies.set('session_id', sessionIdCookie, { path: '/', httpOnly: true, sameSite: "strict" });// used to be sameSite: false
		// cookies.set('session_id', sessionId, { path: '/', httpOnly: true, sameSite: false }); // change sameSite: "strict" (didn't work in Safari in local dev)


		/***** New end? */

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
	// console.log('===> Callback - server - redirecting to "/" <===');
	// redirect(302, "/");
	redirect(302, targetUrl);
	
};
