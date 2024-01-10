
// import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { app_config } from '$lib/server/config';
import { getAccessToken } from '$lib/server/oauth';
const config = await app_config();
// import { get_ms_graph } from '$lib/server/microsoft_graph';

// TBD: add type PageServerLoad here?
export const load: PageServerLoad = async ( {locals } ) => {
	const accessToken = await getAccessToken(locals.sessionData);
	const response = await fetch(`${config.ms_graph_base_uri}/me`, {
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	})
	// const demo_resource = await get_ms_graph('/me');
  // console.log("demo resource - server - health");
  // console.log(health);
	// if (health === null) {
	// 	return error(404, 'Unavailable');
	// }
	// console.log("Hello from routes/playground/ms_graph_me/+page.server.ts");
	const userProfile = await response.json();
	
	return { body: {
		'account': locals.sessionData.account,
		'userProfile': userProfile }
	};
}