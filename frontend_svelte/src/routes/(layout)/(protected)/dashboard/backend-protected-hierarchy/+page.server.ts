import type { PageServerLoad } from './$types';
// import { msalAuthProvider } from '$lib/server/oauth';
// import AppConfig from '$lib/server/config';
// import { error } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis/backendApi';

// const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ locals }) => {
	// const sessionId = locals.sessionData.sessionId;
	// // const sessionId = cookies.get('session_id');
	// if (!sessionId) {
	// 	console.error('routes - protectedResource - page.server - no session id');
	// 	throw error(401, 'No session id!');
	// }
	// const accessToken = await msalAuthProvider.getAccessToken(sessionId, [
	// 	`${appConfig.api_scope}/api.read`,
	// 	'User.Read'
	// ]);
	// const response = await fetch(`${appConfig.backend_origin}/api/v1/protected/resource/`, {
	// 	headers: {
	// 		Authorization: `Bearer ${accessToken}`
	// 	}
	// });

	const sessionId = locals.sessionData.sessionId;
	const response = await backendAPI.get(sessionId, '/protected/resource/');

	return {
		protectedResource: await response.json()
	};
	// console.log("load protected resource data");
};
