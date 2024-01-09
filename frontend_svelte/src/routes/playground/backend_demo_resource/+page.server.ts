import type { PageServerLoad } from './$types';
import { app_config } from '$lib/server/config';

const config = await app_config();

export const load: PageServerLoad = async () => {
	const response = await fetch(`${config.backend_origin}/api/v1/demo_resource`);
	const demoResources = await response.json();
	return { body: demoResources };
};
