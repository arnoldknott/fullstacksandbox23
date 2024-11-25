import { v4 } from 'uuid';
import { msalAuthProvider } from '$lib/server/oauth';
import { redisCache } from '$lib/server/cache';
import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import type { Session } from '$lib/types';
import { user_store } from '$lib/stores';

export const load: PageServerLoad = async ({ url, cookies, request }) => {
	let loginUrl: string;
	try {
		// create the session uuid here:
		const sessionId = `session:${v4()}`;
		const userAgent = request.headers.get('user-agent');
		// Type that one:
		const sessionData: Session = {
			loggedIn: false,
			userAgent: userAgent || ''
		};
		// console.log("=== signin - sessionData, typed ===");
		// console.log(sessionData);

		// const sessionDataJSON = JSON.stringify(sessionData);
		// console.log("=== signin - sessionData, JSON ===");
		// console.log(sessionDataJSON);

		// const sessionDataJSONnative = { "loggedIn": false, "userProfile": {} }
		// console.log("=== signin - sessionDatanative, JSON input ===");
		// console.log(sessionDataJSONnative);

		// const redisClient = await redisCache.provideClient();
		// await redisClient.json.set("typed", "$", Object(sessionData));
		// await redisClient.expire("typed", 3600);

		// await redisClient.json.set("stringified", "$", sessionDataJSON);
		// await redisClient.expire("stringified", 3600);

		// await redisClient.json.set("native", "$", sessionDataJSONnative);
		// await redisClient.expire("native", 3600);

		// move to setSession in $lib/server/cache.ts:
		const redisClient = await redisCache.provideClient();
		await redisClient.json.set(sessionId, '$', Object(sessionData));
		await redisClient.expire(sessionId, 60); // use sessionTimeout from cache.ts

		user_store.set(sessionData);

		// const sessionIdCookie = sessionId.replace("session:", "");
		// cookies.set('session_id', sessionIdCookie, { path: '/', httpOnly: true, sameSite: "strict" });// used to be sameSite: false
		cookies.set('session_id', sessionId, { path: '/', httpOnly: true, sameSite: false }); // change sameSite: "strict" (didn't work in Safari in local dev)

		// await redisCache.setSession(sessionId, '.', sessionData);
		loginUrl = await msalAuthProvider.signIn(sessionId, url.origin);
	} catch (err) {
		console.error('login - server - sign in redirect failed');
		console.error(err);
		throw err;
	}
	redirect(302, loginUrl);
};

// TBD: good template for use with other forms, e.g. chatbot.
// // TBD: add type PageServerLoad here?
// export const actions = {
// 	default: async ({ cookies, request }) => {
// 		const data = await request.formData();
// 		const payloadLogin = {
// 			email: data.get('email')?.toString() || '',
// 			password: data.get('password')?.toString() || ''
// 		};
// 		const accessToken = await postBackend('/api/user/token/', payloadLogin);
// 		let response = {
// 			status: NaN,
// 			body: {},
// 			redirect: ''
// 		};
// 		if (
// 			!accessToken ||
// 			accessToken.token === 'undefined' ||
// 			accessToken.detail === 'Invalid token.'
// 		) {
// 			response = {
// 				status: 401,
// 				body: {
// 					message: 'Unauthorized'
// 				},
// 				redirect: '/login'
// 			};
// 		} else {
// 			const user = await getBackend('/api/user/me/', accessToken.token);
// 			user.loggedIn = true;
// 			user_store.set(user);
// 			cookies.set('accessToken', accessToken.token);
// 			response = {
// 				status: 200,
// 				body: {
// 					message: 'userLoggedIn'
// 				},
// 				redirect: '/dashboard'
// 			};
// 		}
// 		return response;
// 	}
// };
