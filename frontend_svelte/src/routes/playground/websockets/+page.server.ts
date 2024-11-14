import type { PageServerLoad } from './$types';
import AppConfig from '$lib/server/config';

const config = await AppConfig.getInstance();

export const load: PageServerLoad = async () => {
	return {
		backend_fqdn: config.backend_fqdn
	};
};
