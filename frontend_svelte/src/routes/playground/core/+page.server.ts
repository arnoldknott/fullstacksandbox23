import { app_config } from '$lib/core';
import { error } from '@sveltejs/kit';

// TBD: add type PageServerLoad here?
export const load = async () => {
	const configuration = await app_config();

	if (configuration === null) {
		return error(404, 'Unavailable');
	}
	return configuration;
};
