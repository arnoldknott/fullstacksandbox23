import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { Identity } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;

	const payload = { identities: [] as Identity[] };
	const myTeamsIdentities = await microsoftGraph.getAttachedTeamsAsIdentities(
		sessionId,
		locals.sessionData.currentUser?.azure_token_groups
	);
	payload.identities.push(...myTeamsIdentities);
	const allIdentities = await backendAPI.getAllIdentities(sessionId);
	payload.identities.push(...allIdentities);

	return { payload };
};
