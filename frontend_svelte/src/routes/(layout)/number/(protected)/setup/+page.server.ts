import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { AccessPolicy, Identity, NumberExtended } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const payload = {
		numbers: [] as NumberExtended[],
		cursor: 0,
		identities: [] as Identity[]
	};
	const [snapshot, policiesResponse] = await Promise.all([
		backendAPI.getSnapshot<NumberExtended>(
			sessionId,
			'/number/snapshot?include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc'
		),
		backendAPI.get(sessionId, '/access/policy/resource/type/Number')
	]);
	const numbers = snapshot.entities;
	const policies: AccessPolicy[] = policiesResponse.ok ? await policiesResponse.json() : [];
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	for (const number of numbers) {
		number.access_policies = policiesByEntity[number.id] ?? [];
	}
	payload.numbers = numbers;
	payload.cursor = snapshot.cursor;
	// add all linked Microsoft Teams identities:
	const [myTeamsIdentities, allIdentities] = await Promise.all([
		microsoftGraph.getAttachedTeamsAsIdentities(
			sessionId,
			locals.sessionData.currentUser?.azure_token_groups
		),
		backendAPI.getAllIdentities(sessionId)
	]);
	payload.identities.push(...myTeamsIdentities);
	// add all app internal identities (users, ueber-groups, groups, sub-groups, sub-sub-groups):
	payload.identities.push(...allIdentities);
	// add one public identity:
	payload.identities.push({
		id: PUBLIC_IDENTITY_ID,
		name: 'All users',
		type: IdentityType.PUBLIC
	});
	return { payload };
};
