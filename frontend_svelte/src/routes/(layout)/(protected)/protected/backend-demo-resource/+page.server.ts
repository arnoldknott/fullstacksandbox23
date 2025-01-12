import type { Actions, PageServerLoad } from './$types';
// import { msalAuthProvider } from '$lib/server/oauth';
// import AppConfig from '$lib/server/config';
// import { error } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis';
import { fail } from '@sveltejs/kit';
import type { DemoResource, DemoResourceWithCreationDate } from '$lib/types';

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
	console.log('=== routes - demo-resource - page.server - load function executed ===');

	// either send a token or make the demo resource publicly accessible by adding an access policy with flag public=True
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

	const response = await backendAPI.get(sessionId, '/demoresource/');
	const demoResources = await response.json();
	const resourceIds = demoResources.map((resource: DemoResource) => resource.id);
	const creationDataResponse = await backendAPI.post(
		sessionId,
		'/access/log/created',
		JSON.stringify(resourceIds)
	);
	const creationDates = await creationDataResponse.json();
	const demoResourcesWithCreationDates = demoResources.map(
		(resource: DemoResourceWithCreationDate, index: number) => {
			resource = { ...resource };
			resource.creation_date = new Date(creationDates[index]);
			return resource;
		}
	);
	demoResourcesWithCreationDates.sort(
		(a: DemoResourceWithCreationDate, b: DemoResourceWithCreationDate) => {
			return a.creation_date < b.creation_date ? 1 : -1;
		}
	);

	// console.log('=== demoResourcesWithCreationDates ===');
	// console.log(demoResourcesWithCreationDates);

	return { demoResourcesWithCreationDates };
};

export const actions: Actions = {
	post: async ({ locals, request }) => {
		console.log('=== routes - demo-resource - page.server - post function executed ===');
		const data = await request.formData();

		const sessionId = locals.sessionData.sessionId;
		const response = await backendAPI.post(sessionId, '/demoresource/', data);
		if (response.status !== 201) {
			return fail(response.status, { error: response.statusText });
		} else {
			const payload = await response.json();
			return {
				id: payload.id,
				status: 'created'
			};
		}
	},
	put: async ({ locals, request }) => {
		console.log('=== routes - demo-resource - page.server - put function executed ===');
		const data = await request.formData();
		const sessionId = locals.sessionData.sessionId;
		const response = await backendAPI.put(sessionId, `/demoresource/${data.get('id')}`, data);
		if (response.status !== 200) {
			return fail(response.status, { error: response.statusText });
		}
	},
	delete: async ({ locals, request }) => {
		console.log('=== routes - demo-resource - page.server - delete function executed ===');
		const data = await request.formData();
		const sessionId = locals.sessionData.sessionId;
		const response = await backendAPI.delete(sessionId, `/demoresource/${data.get('id')}`);
		if (response.status === 200) {
			return {
				status: 'deleted'
			};
		}
		// if (response.status !== 200) {
		// 	return fail(response.status, { error: response.statusText });
		// }
	}
}; //satisfies Actions;
