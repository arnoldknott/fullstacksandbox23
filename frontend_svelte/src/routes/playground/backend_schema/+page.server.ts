import type { PageServerLoad } from './$types';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async () => {
	// TBD: consider removing the try catch block
	try {
		const response = await fetch(`${appConfig.backend_origin}/openapi.json`);
		const schema = await response.json();
		return { body: schema };
	} catch (err) {
		console.error('playground - backend_schema - server - load - failed');
		console.error(err);
		throw err;
	}
};
