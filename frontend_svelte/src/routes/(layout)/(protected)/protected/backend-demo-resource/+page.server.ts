import type { Actions, PageServerLoad } from './$types';
// import { msalAuthProvider } from '$lib/server/oauth';
// import AppConfig from '$lib/server/config';
// import { error } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis';

// const appConfig = await AppConfig.getInstance();

// function removeEmpty( object: Object ): Object {
// 	console.log("=== object ===");
// 	console.log(object);
// 	return Object.entries(object).reduce((acc: { [key: string]: any }, [key, value]) => {
// 		console.log("=== key ===");
// 		console.log(key);
// 		console.log("=== value ===");
// 		console.log(value);
// 		if (value !== '' && value !== undefined && value !== null) {
// 			acc[key] = typeof value === "object" ? removeEmpty(value) : value;
// 		}
// 		return acc;
// 	}, {});
// }

export const load: PageServerLoad = async ({ locals }) => {
	// either send a token or make the demo resource publically accessable by adding an access policy with flag public=True
	// const sessionId = cookies.get('session_id');
	const sessionId = locals.sessionData.sessionId;

	// before creating a class for backend access:
	// if (!sessionId) {
	// 	throw error(401, 'No session id!');
	// }
	// const accessToken = await msalAuthProvider.getAccessToken(sessionId, [
	// 	`${appConfig.api_scope}/api.read`
	// ]);
	// const response = await fetch(`${appConfig.backend_origin}/api/v1/demoresource/`, {
	// 	headers: {
	// 		Authorization: `Bearer ${accessToken}`
	// 	}
	// });

	const response = await backendAPI.get(sessionId, '/demoresource');
	const demoResources = await response.json();
	return { demoResources };
};

export const actions = {
	post: async ({ locals, request }) => {
		const data = await request.formData();

		// before creating a class for backend access:
		// // console.log('=== data ===');
		// // console.log(data);
		// // const payload =  JSON.stringify(data);
		// const payload = JSON.stringify(Object.fromEntries(data));
		// // console.log('=== payload ===');
		// // console.log(payload);

		// // const sessionId = cookies.get('session_id');
		// const sessionId = locals.sessionData.sessionId;
		// if (!sessionId) {
		// 	console.error('routes - demo-resource - page.server - no session id');
		// 	throw error(401, 'No session id!');
		// }
		// const accessToken = await msalAuthProvider.getAccessToken(sessionId, [
		// 	`${appConfig.api_scope}/api.write`
		// ]);
		// await fetch(`${appConfig.backend_origin}/api/v1/demoresource/`, {
		// 	method: 'POST',
		// 	headers: {
		// 		Authorization: `Bearer ${accessToken}`,
		// 		'Content-Type': 'application/json'
		// 	},
		// 	body: payload
		// });

		// const payload = Object.fromEntries(data);

		const sessionId = locals.sessionData.sessionId;
		await backendAPI.post(sessionId, '/demoresource', data);

		// console.log("=== data ===");
		// console.log(data);
		// const name = data.get('name');
		// console.log("=== name ===");
		// console.log(name);
		// const payload = removeEmpty(data);
		// console.log("=== payload ===");
		// console.log(payload);
	},
	delete: async ({ locals, request }) => {
		const data = await request.formData();

		const sessionId = locals.sessionData.sessionId;
		await backendAPI.delete(sessionId, `/demoresource/${data.get('id')}`);

		// before creating a class for backend
		console.log('=== data ===');
		console.log(data);
	}
} satisfies Actions;
