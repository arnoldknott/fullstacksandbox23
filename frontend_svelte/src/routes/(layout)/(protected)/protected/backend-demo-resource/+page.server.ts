import type { Actions, PageServerLoad } from './$types';
// import { error } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis';
import { fail } from '@sveltejs/kit';
import type {
	AccessPolicy,
	AccessRight,
	DemoResource,
	DemoResourceExtended,
	MicrosoftTeamBasic
} from '$lib/types';
import { microsoftGraph } from '$lib/server/apis';

export const load: PageServerLoad = async ({ locals }) => {
	// console.log('=== routes - demo-resource - page.server - load function executed ===');
	const sessionId = locals.sessionData.sessionId;

	const response = await backendAPI.get(sessionId, '/demoresource/');
	const demoResources = await response.json();
	const demoResourceIds = demoResources.map((resource: DemoResource) => resource.id);
	const creationDataResponse = await backendAPI.post(
		sessionId,
		'/access/log/created',
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

	const accessRightsResponse = await backendAPI.post(
		sessionId,
		'/access/right/resources',
		JSON.stringify(demoResourceIds)
	);
	const accessRights = await accessRightsResponse.json();

	const ownedDemoResourceIds = accessRights
		.filter((right: AccessRight) => right.action === 'own')
		.map((right: AccessRight) => right.resource_id);

	const accessPoliciesResponse = await backendAPI.post(
		sessionId,
		'/access/policy/resources',
		JSON.stringify(ownedDemoResourceIds)
	);
	const accessPolicies: AccessPolicy[] = await accessPoliciesResponse.json();

	const demoResourcesExtended = demoResources.map(
		(resource: DemoResourceExtended, index: number) => {
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
		}
	);
	demoResourcesExtended.sort((a: DemoResourceExtended, b: DemoResourceExtended) => {
		return (a.creation_date ?? 0) < (b.creation_date ?? 0) ? 1 : -1;
	});

	let microsoftTeams: MicrosoftTeamBasic[] = [];
	if (locals.sessionData.userProfile && locals.sessionData.userProfile.azure_token_groups) {
		microsoftTeams = await microsoftGraph.getAttachedTeams(
			sessionId,
			locals.sessionData.userProfile.azure_token_groups
		);
	}

	// let microsoftTeamsExtended = microsoftTeams.map(
	// 	(team: MicrosoftTeamBasic) => {
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
		console.log('=== routes - demo-resource - page.server - share function executed ===');
		const data = await request.formData();
		const accessPolicy = {
			resource_id: data.get('id'),
			identity_id: url.searchParams.get('teamid'),
			action: 'own' // TBD. make this dynamic: own, write, read
		};

		const sessionId = locals.sessionData.sessionId;

		await backendAPI.post(sessionId, '/access/policy', JSON.stringify(accessPolicy));

		// const accessPolicy = {
		// 	resource_id: params.query.get('resource_id'),
		// }
	}
}; //satisfies Actions;
