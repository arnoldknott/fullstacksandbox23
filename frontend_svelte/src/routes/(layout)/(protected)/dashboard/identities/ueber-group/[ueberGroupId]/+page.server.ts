import type { PageServerLoad } from './$types';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { Group, UeberGroup } from '$lib/types';
import type { User as AzureUser } from '@microsoft/microsoft-graph-types';

export const load: PageServerLoad = async ({ parent, locals, params }) => {
	const sessionId = locals.sessionData.sessionId;
	const parentData = await parent();
	console.log('=== Parent Data ===');
	console.log(parentData);

	const responsePayload = {
		thisUeberGroup: {} as UeberGroup,
		allOtherGroups: [] as Group[],
		allUsers: [] as AzureUser[]
	};

	const responseUeberGroups = await backendAPI.get(sessionId, `/uebergroup/${params.ueberGroupId}`);
	if (responseUeberGroups.status === 200) {
		responsePayload.thisUeberGroup = await responseUeberGroups.json();
	} else {
		console.error('Error fetching Ueber Group:', responseUeberGroups.status);
	}

	const responseAllGroups = await backendAPI.get(sessionId, `/group/`);
	if (responseAllGroups.status === 200) {
		const allGroups = await responseAllGroups.json();
		const groupsInUeberGroupIds =
			responsePayload.thisUeberGroup.groups?.map((group: Group) => group.id) ?? [];
		responsePayload.allOtherGroups = allGroups.filter(
			(group: Group) => !groupsInUeberGroupIds.includes(group.id)
		);
	} else {
		console.error('Error fetching all Groups:', responseAllGroups.status);
	}

	if (parentData.session?.currentUser?.azure_token_roles?.includes('Admin')) {
		const responseUsers = await backendAPI.get(sessionId, `/user/`);
		const users = await responseUsers.json();
		if (responseUsers.status === 200) {
			const azureUsers: AzureUser[] = [];
			for (const user of users) {
				const responseAzureUsers = await microsoftGraph.get(
					sessionId,
					`/users/${user.azure_user_id}`
				);
				const azureUser: AzureUser = await responseAzureUsers.json();
				console.log('=== Azure User ===');
				console.log(azureUser);
				azureUsers.push(azureUser);
			}
			responsePayload.allUsers = azureUsers;
		} else {
			console.error('Error fetching Users:', responseUsers.status);
		}
	}

	return { ...responsePayload };
};
