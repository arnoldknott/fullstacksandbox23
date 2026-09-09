import type { User as MicrosoftUser } from '@microsoft/microsoft-graph-types';
import { error } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import { MicrosoftAccountLinking } from '$lib/server/apis/integrations';
import type { GroupExtended, Hierarchy, UeberGroupExtended } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ parent, locals, params }) => {
	const sessionId = locals.sessionData.sessionId;
	const parentData = await parent();

	const responsePayload = {
		thisUeberGroup: {} as UeberGroupExtended,
		ueberGroupCursor: 0,
		linkedMicrosoftUsers: [] as MicrosoftUser[],
		// allOtherGroups: [] as Group[],
		allGroups: [] as GroupExtended[],
		groupCursor: 0,
		allMicrosoftUsers: [] as MicrosoftUser[]
		// allOtherMicrosoftUsers: [] as MicrosoftUser[]
	};

	const snapshotQuery =
		'?include=creation-date&include=access-right&sort=creation-date&direction=desc';
	const [ueberGroupSnapshot, groupSnapshot, hierarchiesResponse] = await Promise.all([
		backendAPI.getSnapshot<UeberGroupExtended>(sessionId, '/uebergroup/snapshot' + snapshotQuery),
		backendAPI.getSnapshot<GroupExtended>(sessionId, '/group/snapshot' + snapshotQuery),
		backendAPI.get(sessionId, '/access/hierarchies?parent-id=' + params.ueberGroupId)
	]);
	if (!hierarchiesResponse.ok) {
		error(502, 'Identity snapshots could not be loaded');
	}
	const thisUeberGroup = ueberGroupSnapshot.entities.find(
		(group) => group.id === params.ueberGroupId
	);
	if (!thisUeberGroup) error(404, 'Ueber group could not be loaded');
	const hierarchies = (await hierarchiesResponse.json()) as Hierarchy[];
	const hierarchiesByGroup = Object.groupBy(hierarchies, (hierarchy) => hierarchy.child_id);
	for (const group of groupSnapshot.entities) {
		group.hierarchies = hierarchiesByGroup[group.id] ?? [];
	}
	responsePayload.thisUeberGroup = thisUeberGroup;
	responsePayload.ueberGroupCursor = ueberGroupSnapshot.cursor;
	responsePayload.allGroups = groupSnapshot.entities;
	responsePayload.groupCursor = groupSnapshot.cursor;

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
