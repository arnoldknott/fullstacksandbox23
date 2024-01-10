import type { PageServerLoad } from './$types';
import { getAccessToken } from '$lib/server/oauth';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ fetch, locals }) => {
	const accessToken = await getAccessToken(locals.sessionData);
	const response = await fetch(`${appConfig.backend_origin}/api/v1/protected_resource/`, {
		headers: {
      Authorization: `Bearer ${accessToken}`
    }
	})

	return {
		protectedResource: await response.json()
	}
	// console.log("load protected resource data");
};