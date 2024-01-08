
// import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
// import { get_ms_graph } from '$lib/server/microsoft_graph';

// TBD: add type PageServerLoad here?
export const load: PageServerLoad = async () => {
	// const demo_resource = await get_ms_graph('/me');
  // console.log("demo resource - server - health");
  // console.log(health);
	// if (health === null) {
	// 	return error(404, 'Unavailable');
	// }
	console.log("Hello from routes/playground/ms_graph_me/+page.server.ts");
	// return { body: demo_resource };
};
