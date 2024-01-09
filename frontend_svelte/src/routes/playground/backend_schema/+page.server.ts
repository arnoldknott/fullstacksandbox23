import type { PageServerLoad } from './$types';
import { app_config} from '$lib/server/config';
const config = await app_config();

export const load: PageServerLoad = async () => {
	// TBD: consider removing the try catch block
	try {
		const response = await fetch(`${config.backend_origin}/openapi.json`);
		const schema = await response.json();
		return { body: schema };
	} catch (err) {
		console.error('playground - backend_schema - server - load - failed');
		console.error(err);
		throw err;
	}
};
