import type { Actions, PageServerLoad } from './$types';
import { msalAuthProvider } from '$lib/server/oauth';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

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

export const load: PageServerLoad = async ({ fetch, locals }) => {
	// either send a token or make the demo resource publically accessable by adding an access policy with flag public=True
	const accessToken = await msalAuthProvider.getAccessToken(locals.sessionData, [
		`${appConfig.api_scope}/api.read`
	]);
	const response = await fetch(`${appConfig.backend_origin}/api/v1/demoresource/`, {
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	});
	const demoResources = await response.json();
	return { demoResources };
};

export const actions = {
	default: async ({ locals, request }) => {
		const data = await request.formData();

		console.log('=== data ===');
		console.log(data);
		// const payload =  JSON.stringify(data);
		const payload = JSON.stringify(Object.fromEntries(data));
		console.log('=== payload ===');
		console.log(payload);

		const accessToken = await msalAuthProvider.getAccessToken(locals.sessionData, [
			`${appConfig.api_scope}/api.write`
		]);
		await fetch(`${appConfig.backend_origin}/api/v1/demoresource/`, {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${accessToken}`,
				'Content-Type': 'application/json'
			},
			body: payload
		});
		// console.log("=== data ===");
		// console.log(data);
		// const name = data.get('name');
		// console.log("=== name ===");
		// console.log(name);
		// const payload = removeEmpty(data);
		// console.log("=== payload ===");
		// console.log(payload);
	}
} satisfies Actions;
