import type { PageServerLoad } from './$types';
import { getAccessToken } from '$lib/server/oauth';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ fetch, locals }) => {
	const accessToken = await getAccessToken(locals.sessionData, [
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
