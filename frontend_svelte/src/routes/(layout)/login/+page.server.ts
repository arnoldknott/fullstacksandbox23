import { v4 } from 'uuid';
import { msalAuthProvider } from '$lib/server/oauth';
import { redisCache } from '$lib/server/cache';
import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import type { Session } from '$lib/types';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ url, cookies, request }) => {
	let loginUrl: string;
	try {
		// create the session uuid here:
		const sessionId = v4();
		const userAgent = request.headers.get('user-agent');
		// Type that one:
		const sessionData: Session = {
			status: 'authentication_pending',
			loggedIn: false,
			userAgent: userAgent || ''
		};

		// move to setSession in $lib/server/cache.ts:
		// const redisClient = await redisCache.provideClient();
		// await redisClient.json.set(sessionId, '$', Object(sessionData));
		// await redisClient.expire(sessionId, sessionTimeout); // use sessionTimeout from cache.ts
		await redisCache.setSession(
			sessionId,
			'$',
			JSON.stringify(sessionData),
			appConfig.authentication_timeout
		);

		cookies.set('session_id', sessionId, {
			path: '/',
			httpOnly: true,
			sameSite: false, // TBD: change to strict for production!
			// secure: true,// TBD: add this in for production!
			maxAge: appConfig.authentication_timeout
		}); // change sameSite: "strict" (didn't work in Safari in local dev)

		const targetURL = url.searchParams.get('targetURL') || undefined;
		// console.log('🚪 login - server - targetURL')
		// console.log(targetURL);

		loginUrl = await msalAuthProvider.signIn(sessionId, url.origin, targetURL);
	} catch (err) {
		console.error('🔥 🚪 login - server - sign in redirect failed');
		console.error(err);
		throw err; // TBD consider redirect to "/" instead here?
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
