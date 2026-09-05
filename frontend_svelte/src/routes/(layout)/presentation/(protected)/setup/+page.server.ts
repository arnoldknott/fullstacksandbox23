import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { AccessPolicy, Identity, PresentationExtended } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const payload = {
		presentations: [] as PresentationExtended[],
		cursor: 0,
		identities: [] as Identity[]
	};
	const [snapshotResponse, policiesResponse] = await Promise.all([
		backendAPI.get(
			sessionId,
			'/presentation/snapshot?include=creation_date&include=last_modified_date&include=access_right&sort=creation_date&direction=desc'
		),
		backendAPI.get(sessionId, '/access/policy/resource/type/Presentation')
	]);
	if (!snapshotResponse.ok) {
		error(snapshotResponse.status, 'Presentations could not be loaded');
	}
	const cursor = snapshotResponse.headers.get('X-Entity-Cursor');
	if (cursor === null) {
		error(502, 'Presentation snapshot did not include a cursor');
	}
	const presentations: PresentationExtended[] = await snapshotResponse.json();
	const policies: AccessPolicy[] = policiesResponse.ok ? await policiesResponse.json() : [];
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	for (const presentation of presentations) {
		presentation.access_policies = policiesByEntity[presentation.id] ?? [];
	}
	payload.presentations = presentations;
	payload.cursor = Number.parseInt(cursor, 10);
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
		id: PUBLIC_IDENTITY_ID,
		name: 'All users',
		type: IdentityType.PUBLIC
	});
	return { payload };
};
