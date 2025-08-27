import type { PageServerLoad } from './$types';
import { backendAPI } from '$lib/server/apis/backendApi';
import type { Group, UeberGroup } from '$lib/types';

export const load: PageServerLoad = async ({ locals, params }) => {
	const sessionId = locals.sessionData.sessionId;

	const responsePayload = {
		thisUeberGroup: {} as UeberGroup,
		allOtherGroups: [] as Group[]
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

	return { ...responsePayload };
};
