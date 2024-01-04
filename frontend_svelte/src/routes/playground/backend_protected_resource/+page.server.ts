// import { getBackend } from '$lib/backend';
// // import { error } from '@sveltejs/kit';
// import type { PageServerLoad } from './$types';

// // TBD: add type PageServerLoad here?
// export const load: PageServerLoad = async () => {
// 	const health = await getBackend('/api/v1/protected_resource');
//   // console.log("demo resource - server - health");
//   // console.log(health);
// 	// if (health === null) {
// 	// 	return error(404, 'Unavailable');
// 	// }
// 	return { body: health };
// };

console.log("Hello from routes/playground/backend_protected_resource/+page.server.ts");

// console.log(request)

// import type { Actions } from './$types';

// export const actions = {
// 	default: async (event) => {
// 		console.log("backend_protected_resource - server - event");
//     console.log(event);
// 	},
// } satisfies Actions;
