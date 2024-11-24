import type { PageServerLoad } from './$types';
import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth';

const appConfig = await AppConfig.getInstance();

// TBD: add type PageServerLoad here?
export const load: PageServerLoad = async ({ locals, cookies }) => {
	const sessionId = cookies.get('session_id');
	if (!sessionId) {
		console.error('routes - playground - ms_graph_me - page.server - no session id');
		throw Error('401', 'No session id!');
	}
	const accessToken = await msalAuthProvider.getAccessToken(sessionId, locals.sessionData, [
		'User.Read'
	]);
	const response = await fetch(`${appConfig.ms_graph_base_uri}/me`, {
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	});
	// const demo_resource = await get_ms_graph('/me');
	// console.log("demo resource - server - health");
	// console.log(health);
	// if (health === null) {
	// 	return error(404, 'Unavailable');
	// }
	// console.log("Hello from routes/playground/ms_graph_me/+page.server.ts");
	const userProfile = await response.json();

	return {
		account: locals.sessionData.account,
		userProfile: userProfile
	};
};
