import type { PageServerLoad } from './$types';
// TBD: consider using backend.ts for getting accessToken from sessionData
import { getAccessToken } from '$lib/server/oauth';
import { app_config } from '$lib/server/config';

const config = await app_config();

export const load: PageServerLoad = async ({ fetch, locals }) => {
	const accessToken = await getAccessToken(locals.sessionData);
	const response = await fetch(`${config.backend_origin}/api/v1/protected_resource/`, {
		headers: {
      Authorization: `Bearer ${accessToken}`
    }
	})

	return {
		protectedResource: await response.json()
	}
	// console.log("load protected resource data");
};