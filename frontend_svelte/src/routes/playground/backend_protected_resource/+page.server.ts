import { getBackend } from '$lib/backend';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	const protected_resources = await getBackend('/api/v1/protected_resource')
	return { body: protected_resources };
};

