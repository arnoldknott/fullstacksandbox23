import type { PageServerLoad } from './$types';
import { getAccessToken } from '$lib/server/oauth';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ fetch, locals }) => {
	// either send a token or make the demo resource publically accessable by adding an access policy with flag public=True
	const accessToken = await getAccessToken(locals.sessionData, [`${appConfig.api_scope}/api.read`]);
	const response = await fetch(`${appConfig.backend_origin}/api/v1/demoresource/`, {
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	});
	const demoResources = await response.json();
	return { body: demoResources };
};
