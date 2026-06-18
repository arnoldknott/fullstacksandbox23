import { fail } from '@sveltejs/kit';

import { Action } from '$lib/accessHandler';
// import { error } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis/backendApi';
// import { Action } from '$lib/accessHandler';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { AccessPolicy, DemoResource, DemoResourceExtended, Identity } from '$lib/types';

import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	// console.log('=== routes - demo-resource - page.server - load function executed ===');
	const sessionId = locals.sessionData.sessionId;

	const payload = { demoResources: [] as DemoResourceExtended[], identities: [] as Identity[] };

	const response = await backendAPI.get(sessionId, '/demoresource/');
	let demoResourcesExtended = [];
	if (response.status === 200) {
		const demoResources = await response.json();
		const demoResourceIds = demoResources.map((resource: DemoResource) => resource.id);
		const creationDataResponse = await backendAPI.post(
			sessionId,
			'/access/logs/created',
			JSON.stringify(demoResourceIds)
		);
		const creationDates = await creationDataResponse.json();

		// let demoResourcesExtended = demoResources.map(
		// 	(resource: DemoResourceExtended, index: number) => {
		// 		resource = { ...resource };
		// 		resource.creation_date = new Date(creationDates[index]);
		// 		return resource;
		// 	}
		// );

		// Fetch access rights of current user for the demo resources
		const accessRightsResponse = await backendAPI.post(
			sessionId,
			'/access/right/resources',
			JSON.stringify(demoResourceIds)
		);
		const accessRights: (Action | null)[] = await accessRightsResponse.json();

		// Get other users access policies for all demo resources, where user has 'own' rights:
		const ownedDemoResourceIds = demoResourceIds.filter(
			(_: string, index: number) => accessRights[index] === Action.OWN
		);

		const accessPoliciesResponse = await backendAPI.post(
			sessionId,
			'/access/policy/resources',
			JSON.stringify(ownedDemoResourceIds)
		);
		const accessPolicies: AccessPolicy[] = await accessPoliciesResponse.json();

		demoResourcesExtended = demoResources.map((resource: DemoResourceExtended, index: number) => {
			// const policies: AccessPolicy[] = accessPolicies.filter((policy: AccessPolicy) => policy.resource_id === resource.id);
			return Object.assign(
				{},
				{
					...resource,
					creation_date: new Date(creationDates[index]),
					access_right: accessRights[index],
					access_policies: accessPolicies.filter(
						(policy: AccessPolicy) => policy.resource_id === resource.id
					)
				}
			);
		});
		demoResourcesExtended.sort((a: DemoResourceExtended, b: DemoResourceExtended) => {
			return (a.creation_date ?? 0) < (b.creation_date ?? 0) ? 1 : -1;
		});
	}
	payload.demoResources = demoResourcesExtended;

	const microsoftTeamsIdentities = await microsoftGraph.getAttachedTeamsAsIdentities(
		sessionId,
		locals.sessionData.currentUser?.azure_token_groups
	);
	payload.identities.push(...microsoftTeamsIdentities);
	const allIdentities = await backendAPI.getAllIdentities(sessionId);
	payload.identities.push(...allIdentities);

	return { payload };
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
			const createdLogResponse = await backendAPI.get(
				sessionId,
				`/access/log/${payload.id}/created`
			);
			const createdLogData = await createdLogResponse.json();

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
	},
	share: async ({ locals, request, url }) => {
		const data = await request.formData();
		const sessionId = locals.sessionData.sessionId;

		return backendAPI.share(
			sessionId,
			data.get('id')?.toString(),
			url.searchParams.get('identity-id')?.toString(),
			url.searchParams.get('action')?.toString(),
			url.searchParams.get('new-action')?.toString()
		);
	}
}; //satisfies Actions;
