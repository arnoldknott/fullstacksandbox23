import type { PageServerLoad } from './$types';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async () => {
	const response = await fetch(`${appConfig.backend_origin}/api/v1/demo_resource`);
	const demoResources = await response.json();
	return { body: demoResources };
};
