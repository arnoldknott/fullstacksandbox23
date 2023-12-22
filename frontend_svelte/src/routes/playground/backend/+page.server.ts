import { getBackend } from '$lib/backend';
import { error } from '@sveltejs/kit';

// TBD: add type PageServerLoad here?
export const load = async () => {
	const schema = await getBackend('/openapi.json');

	if (schema === null) {
		return error(404, 'Unavailable');
	}
	return schema;
};
