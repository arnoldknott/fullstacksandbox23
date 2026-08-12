import AppConfig from '$lib/server/config';

import type { PageServerLoad } from './$types';

const config = await AppConfig.getInstance();

export const load: PageServerLoad = async () => {
	return {
		backend_fqdn: config.backend_fqdn
	};
};
