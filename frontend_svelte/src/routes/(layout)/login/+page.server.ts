import { v4 } from 'uuid';
import { msalAuthProvider } from '$lib/server/oauth';
import { redisCache } from '$lib/server/cache';
import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import type { Session } from '$lib/types';

export const load: PageServerLoad = async ({ url, cookies, request }) => {
	let loginUrl: string;
	try {
		/*****  Used previously: */

		// create the session uuid here:
		const sessionId = `session:${v4()}`;
		const userAgent = request.headers.get('user-agent');
		// Type that one:
		const sessionData: Session = {
			loggedIn: false,
			userAgent: userAgent || ''
		};

		// move to setSession in $lib/server/cache.ts:
		const redisClient = await redisCache.provideClient();
		await redisClient.json.set(sessionId, '$', Object(sessionData));
		await redisClient.expire(sessionId, 20); // use sessionTimeout from cache.ts

		// const sessionIdCookie = sessionId.replace("session:", "");
		// cookies.set('session_id', sessionIdCookie, { path: '/', httpOnly: true, sameSite: "strict", secure: true });// used to be sameSite: false
		cookies.set('session_id', sessionId, { path: '/', httpOnly: true, sameSite: false }); // change sameSite: "strict" (didn't work in Safari in local dev)

		// await redisCache.setSession(sessionId, '.', sessionData);

		/******/

		const targetURL = url.searchParams.get('targetURL') || undefined;

		loginUrl = await msalAuthProvider.signIn(sessionId, url.origin, targetURL);
	} catch (err) {
		console.error('login - server - sign in redirect failed');
		console.error(err);
		throw err;
	}
	// console.log('===> login - server - redirecting to loginUrl <===');
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
