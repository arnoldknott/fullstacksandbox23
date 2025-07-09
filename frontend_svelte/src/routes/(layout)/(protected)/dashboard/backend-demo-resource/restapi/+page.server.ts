import type { Actions, PageServerLoad } from './$types';
// import { error } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis/backendApi';
import { fail } from '@sveltejs/kit';
import type {
	AccessPolicy,
	AccessRight,
	DemoResource,
	DemoResourceExtended,
} from '$lib/types';
import type { Team as MicrosoftTeam } from '@microsoft/microsoft-graph-types';
// import { Action } from '$lib/accessHandler';
import { microsoftGraph } from '$lib/server/apis/msgraph';

export const load: PageServerLoad = async ({ locals }) => {
	// console.log('=== routes - demo-resource - page.server - load function executed ===');
	const sessionId = locals.sessionData.sessionId;

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
		const accessRights = await accessRightsResponse.json();

		// Get other users access policies for all demo resources, where user has 'own' rights:
		const ownedDemoResourceIds = accessRights
			.filter((right: AccessRight) => right.action === 'own')
			.map((right: AccessRight) => right.resource_id);

		const accessPoliciesResponse = await backendAPI.post(
			sessionId,
			'/access/policy/resources',
			JSON.stringify(ownedDemoResourceIds)
		);
		const accessPolicies: AccessPolicy[] = await accessPoliciesResponse.json();

		demoResourcesExtended = demoResources.map((resource: DemoResourceExtended, index: number) => {
			// const userRight = accessRights.find((right: AccessRight) => right.resource_id === resource.id);
			// const policies: AccessPolicy[] = accessPolicies.filter((policy: AccessPolicy) => policy.resource_id === resource.id);
			return Object.assign(
				{},
				{
					...resource,
					creation_date: new Date(creationDates[index]),
					user_right: accessRights.find((right: AccessRight) => right.resource_id === resource.id)
						.action,
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

	// Fetch the Microsoft Teams the user is attached to
	let microsoftTeams: MicrosoftTeam[] = [];
	if (locals.sessionData.currentUser && locals.sessionData.currentUser.azure_token_groups) {
		microsoftTeams = await microsoftGraph.getAttachedTeams(
			sessionId,
			locals.sessionData.currentUser.azure_token_groups
		);
	}

	// let microsoftTeamsExtended = microsoftTeams.map(
	// 	(team: MicrosoftTeam) => {
	// 		// const policies: AccessPolicy[] = accessPolicies.filter((policy: AccessPolicy) => policy.identity_id === team.id);
	// 		return {
	// 			...team,
	// 			// access_policies: accessPolicies.filter((policy: AccessPolicy) => policy.identity_id === team.id)
	// 		};
	// 	}
	// );

	// return { demoResourcesExtended, microsoftTeamsExtended };
	return { demoResourcesExtended, microsoftTeams };
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
