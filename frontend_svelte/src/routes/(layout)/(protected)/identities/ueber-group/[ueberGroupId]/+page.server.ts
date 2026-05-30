import type { User as MicrosoftUser } from '@microsoft/microsoft-graph-types';

import { backendAPI } from '$lib/server/apis/backendApi';
import { MicrosoftAccountLinking } from '$lib/server/apis/integrations';
// import type { Group, UeberGroup, User } from '$lib/types';
import type { Group, UeberGroup } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ parent, locals, params }) => {
	const sessionId = locals.sessionData.sessionId;
	const parentData = await parent();

	const responsePayload = {
		thisUeberGroup: {} as UeberGroup,
		linkedMicrosoftUsers: [] as MicrosoftUser[],
		// allOtherGroups: [] as Group[],
		allGroups: [] as Group[],
		allMicrosoftUsers: [] as MicrosoftUser[]
		// allOtherMicrosoftUsers: [] as MicrosoftUser[]
	};

	const responseUeberGroup = await backendAPI.get(sessionId, `/uebergroup/${params.ueberGroupId}`);
	if (responseUeberGroup.status === 200) {
		responsePayload.thisUeberGroup = await responseUeberGroup.json();
	} else {
		console.error('Error fetching Ueber Group:', responseUeberGroup.status);
	}

	const responseAllGroups = await backendAPI.get(sessionId, `/group/`);
	if (responseAllGroups.status === 200) {
		responsePayload.allGroups = await responseAllGroups.json();
		// const allGroups = await responseAllGroups.json();
		// const groupsInUeberGroupIds =
		// 	responsePayload.thisUeberGroup.groups?.map((group: Group) => group.id) ?? [];
		// responsePayload.allOtherGroups = allGroups.filter(
		// 	(group: Group) => !groupsInUeberGroupIds.includes(group.id)
		// );
	} else {
		console.error('Error fetching all Groups:', responseAllGroups.status);
	}

	if (parentData.session?.currentUser?.azure_token_roles?.includes('Admin')) {
		const responseUsers = await backendAPI.get(sessionId, `/user/`);
		// const usersInUeberGroupIds =
		// 	responsePayload.thisUeberGroup.users?.map((user: User) => user.id) ?? [];
		// const linkedUsers = users.filter((user: User) => usersInUeberGroupIds.includes(user.id));
		// const allOtherUsers = users.filter((user: User) => !usersInUeberGroupIds.includes(user.id));
		if (responseUsers.status === 200) {
			const users = await responseUsers.json();
			responsePayload.allMicrosoftUsers = await MicrosoftAccountLinking.getUsers(sessionId, users);
			// 	const linkedMicrosoftUsers = await MicrosoftAccountLinking.getUsers(sessionId, linkedUsers);
			// 	responsePayload.linkedMicrosoftUsers = linkedMicrosoftUsers;
			// 	const allOtherMicrosoftUsers = await MicrosoftAccountLinking.getUsers(
			// 		sessionId,
			// 		allOtherUsers
			// 	);
			// 	responsePayload.allOtherMicrosoftUsers = allOtherMicrosoftUsers;
		} else {
			console.error('Error fetching Users:', responseUsers.status);
		}
	}

	return { ...responsePayload };
};
