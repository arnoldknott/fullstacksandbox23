import type { PageServerLoad } from './$types';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ url }) => {
	const response = await fetch(`${appConfig.backend_origin}/api/v1/core/health`);
	const configuration = await response.json();
	return { body: { keyvaultHealthBackend: configuration, urlServer: url.href } };
};
