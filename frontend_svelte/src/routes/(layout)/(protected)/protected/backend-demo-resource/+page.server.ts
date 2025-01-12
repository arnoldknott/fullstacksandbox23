import type { Actions, PageServerLoad } from './$types';
// import { error } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis';
import { fail } from '@sveltejs/kit';
import type { DemoResource, DemoResourceWithCreationDate } from '$lib/types';

export const load: PageServerLoad = async ({ locals }) => {
	// console.log('=== routes - demo-resource - page.server - load function executed ===');
	const sessionId = locals.sessionData.sessionId;

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

	return { demoResourcesWithCreationDates };
};

export const actions: Actions = {
	post: async ({ locals, request }) => {
		// console.log('=== routes - demo-resource - page.server - post function executed ===');
		const data = await request.formData();

		const sessionId = locals.sessionData.sessionId;
		const response = await backendAPI.post(sessionId, '/demoresource/', data);
		if (response.status !== 201) {
			return fail(response.status, { error: response.statusText });
		} else {
			const payload = await response.json();
			console.log('=== routes - demo-resource - page.server - post function - payload ===');
			console.log(payload);
			const createdLogResponse = await backendAPI.get(
				sessionId,
				`/access/log/${payload.id}/created`
			);
			const createdLogData = await createdLogResponse.json();
			console.log('=== routes - demo-resource - page.server - post function - createdLogData ===');
			console.log(createdLogData);

			return {
				id: payload.id,
				creationDate: createdLogData
			};
		}
	},
	put: async ({ locals, request }) => {
		// console.log('=== routes - demo-resource - page.server - put function executed ===');
		const data = await request.formData();
		const sessionId = locals.sessionData.sessionId;
		const response = await backendAPI.put(sessionId, `/demoresource/${data.get('id')}`, data);
		if (response.status !== 200) {
			return fail(response.status, { error: response.statusText });
		}
	},
	delete: async ({ locals, request }) => {
		// console.log('=== routes - demo-resource - page.server - delete function executed ===');
		const data = await request.formData();
		const sessionId = locals.sessionData.sessionId;
		await backendAPI.delete(sessionId, `/demoresource/${data.get('id')}`);
		// const response = await backendAPI.delete(sessionId, `/demoresource/${data.get('id')}`);
		// if (response.status === 200) {
		// 	return {
		// 		status: 'deleted'
		// 	};
		// }
		// if (response.status !== 200) {
		// 	return fail(response.status, { error: response.statusText });
		// }
	}
}; //satisfies Actions;
