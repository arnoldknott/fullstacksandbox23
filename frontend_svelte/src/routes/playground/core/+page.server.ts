import { app_config } from '$lib/config';
import { error } from '@sveltejs/kit';

// TBD: add type PageServerLoad here?
// export const load = async ( {fetch, session, context } ) => {
	// const host = context.host;
export const load = async (  ) => {
	const configuration = await app_config();

	if (configuration === null) {
		return error(404, 'Unavailable');
	}
	return configuration;
};
