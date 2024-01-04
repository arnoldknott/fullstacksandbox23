import { app_config } from '$lib/server/config';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

// TBD: add type PageServerLoad here?
// export const load = async ( {fetch, session, context } ) => {
	// const host = context.host;
export const load: PageServerLoad = async ( { url } ) => {
	const configuration =  await app_config()
	
	// console.log( url );// URL is needed to generate the redirect URL!
	if (configuration === null) {
		return error(404, 'Unavailable');
	}

	return { keyvaultHealth: configuration.keyvault_health, url: url.toString() };
};
