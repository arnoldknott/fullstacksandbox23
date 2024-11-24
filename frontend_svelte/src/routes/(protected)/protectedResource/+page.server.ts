import type { PageServerLoad } from './$types';
import { msalAuthProvider } from '$lib/server/oauth';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ fetch, locals, cookies }) => {
	const sessionId = cookies.get('session_id');
	if (!sessionId) {
		console.error('routes - protectedResource - page.server - no session id');
		throw Error('401', 'No session id!');
	}
	const accessToken = await msalAuthProvider.getAccessToken(sessionId, locals.sessionData, [
		`${appConfig.api_scope}/api.read`,
		'User.Read'
	]);
	const response = await fetch(`${appConfig.backend_origin}/api/v1/protected/resource/`, {
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	});

	return {
		protectedResource: await response.json()
	};
	// console.log("load protected resource data");
};
