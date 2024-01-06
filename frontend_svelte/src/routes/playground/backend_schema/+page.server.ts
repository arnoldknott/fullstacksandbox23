import { getBackend } from '$lib/backend';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

// TBD: add type PageServerLoad here?
export const load: PageServerLoad = async () => {
	const schema = await getBackend('/openapi.json');

	if (schema === null) {
		return error(404, 'Unavailable');
	}
	return { body: schema };
};
