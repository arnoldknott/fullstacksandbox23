import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { DemoResourceExtended, Identity } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;

	const payload = {
		identities: [] as Identity[],
		entities: [] as DemoResourceExtended[],
		cursor: 0
	};
	const snapshotResponse = await backendAPI.get(
		sessionId,
		'/demoresource/snapshot?include=creation_date&include=last_modified_date&include=access_right&sort=creation_date&direction=desc'
	);
	if (!snapshotResponse.ok) {
		error(snapshotResponse.status, 'Demo resources could not be loaded');
	}
	const cursor = snapshotResponse.headers.get('X-Entity-Cursor');
	if (cursor === null) {
		error(502, 'Demo resource snapshot did not include a cursor');
	}
	payload.entities = await snapshotResponse.json();
	payload.cursor = Number.parseInt(cursor, 10);

	const myTeamsIdentities = await microsoftGraph.getAttachedTeamsAsIdentities(
		sessionId,
		locals.sessionData.currentUser?.azure_token_groups
	);
	// all linked teams identities:
	payload.identities.push(...myTeamsIdentities);
	// all app internal identities (users, ueber-groups, groups, sub-groups, sub-sub-groups):
	const allIdentities = await backendAPI.getAllIdentities(sessionId);
	payload.identities.push(...allIdentities);
	// one public identity:
	payload.identities.push({
		id: PUBLIC_IDENTITY_ID,
		name: 'All users',
		type: IdentityType.PUBLIC
	});

	return { payload };
};
