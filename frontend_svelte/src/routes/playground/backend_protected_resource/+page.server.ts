import { getBackend } from '$lib/backend';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	const protected_resource = await getBackend('/api/v1/protected_resource')
	return { body: protected_resource };
};

