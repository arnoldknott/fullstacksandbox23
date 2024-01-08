import { getBackend } from '$lib/backend';
// import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

// TBD: add type PageServerLoad here?
export const load: PageServerLoad = async () => {
	const demo_resource = await getBackend('/api/v1/demo_resource');
  // console.log("demo resource - server - health");
  // console.log(health);
	// if (health === null) {
	// 	return error(404, 'Unavailable');
	// }
	return { body: demo_resource };
};