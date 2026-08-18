import { IdentityType } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { Identity, Presentation } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const payload = {
		presentations: [] as Presentation[],
		identities: [] as Identity[]
	};
	const responsePresentations = await backendAPI.get(sessionId, '/presentation/');
	if (responsePresentations.status === 200) {
		const presentationsData = await responsePresentations.json();
		payload.presentations = presentationsData;
	}
	// add all linked Microsoft Teams identities:
	const myTeamsIdentities = await microsoftGraph.getAttachedTeamsAsIdentities(
		sessionId,
		locals.sessionData.currentUser?.azure_token_groups
	);
	payload.identities.push(...myTeamsIdentities);
	// add all app internal identities (users, ueber-groups, groups, sub-groups, sub-sub-groups):
	const allIdentities = await backendAPI.getAllIdentities(sessionId);
	payload.identities.push(...allIdentities);
	// add one public identity:
	payload.identities.push({
		id: undefined,
		name: 'All users',
		type: IdentityType.PUBLIC
	});
	return { payload };
};
