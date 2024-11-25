import type { PageServerLoad } from './$types';
// import { signOut } from '$lib/server/oauth';
import { redisCache } from '$lib/server/cache';
import { redirect } from '@sveltejs/kit';
// import {redirect} from '@sveltejs/kit';
import AppConfig from '$lib/server/config';
import { user_store } from '$lib/stores';
const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ url, cookies }) => {
	// console.log("IMPLEMENT logout!");
	const sessionId = cookies.get('session_id');
	cookies.delete('session_id', {
		path: '/',
		expires: new Date(0)
	});
	user_store.set(undefined);
	// TBD: delete set loggedIn to false in redis?
	if (!sessionId) {
		console.error('🔥 logout - server - missing session_id');
		redirect(307, '/');
	}
	const redisClient = await redisCache.provideClient();
	await redisClient.json.set(sessionId, '$.loggedIn', false);
	// signOut();
	redirect(307, `${appConfig.az_logout_uri}?post_logout_redirect_uri=${url.origin}/`);
	// 	// redirect(302, "/");
	// 	return {
	// 		location: "/",
	// 		body: {
	// 			loggedIn: false,
	// 			userProfile: undefined,
	// 			userAgent: undefined
	// 		}
	// };
};

// import type { PageServerLoad } from './$types';

// // export const load: PageServerLoad = async ({ cookies }) => {
// export const load: PageServerLoad = async ({  }) => {
// 	// cookies.delete('accessToken');
// };
