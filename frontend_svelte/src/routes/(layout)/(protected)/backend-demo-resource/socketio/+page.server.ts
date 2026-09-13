import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { AccessPolicy, DemoResourceExtended, Identity } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;

	const payload = {
		identities: [] as Identity[],
		entities: [] as DemoResourceExtended[],
		cursor: 0
	};
	const timeBeforeSnapshotAndPolicies = new Date();
	console.log('=== demo-resource - socketio - timeBeforeSnapshotAndPolicies ===');
	console.log(timeBeforeSnapshotAndPolicies);
	const [snapshot, policiesResponse] = await Promise.all([
		backendAPI.getSnapshot<DemoResourceExtended>(
			sessionId,
			'/demoresource/snapshot?include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc'
		),
		backendAPI.get(sessionId, '/access/policy/resource/type/DemoResource')
	]);
	const timeAfterSnapshotAndPolicies = new Date();
	console.log('=== demo-resource - socketio - timeAfterSnapshotAndPolicies ===');
	console.log(timeAfterSnapshotAndPolicies);
	if (!policiesResponse.ok) {
		error(policiesResponse.status, 'DemoResource access policies could not be loaded');
	}
	const policies: AccessPolicy[] = await policiesResponse.json();
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	for (const entity of snapshot.entities) {
		entity.access_policies = policiesByEntity[entity.id] ?? [];
	}
	payload.entities = snapshot.entities;
	payload.cursor = snapshot.cursor;

	const timeBeforeMicrosoftTeams = new Date();
	console.log('=== demo-resource - socketio - timeBeforeMicrosoftTeams ===');
	console.log(timeBeforeMicrosoftTeams);
	const myTeamsIdentities = await microsoftGraph.getAttachedTeamsAsIdentities(
		sessionId,
		locals.sessionData.currentUser?.azure_token_groups
	);
	const timeAfterMicrosoftTeams = new Date();
	console.log('=== demo-resource - socketio - timeAfterMicrosoftTeams ===');
	console.log(timeAfterMicrosoftTeams);
	// all linked teams identities:
	payload.identities.push(...myTeamsIdentities);
	// all app internal identities (users, ueber-groups, groups, sub-groups, sub-sub-groups):
	const timeBeforeAllIdentities = new Date();
	console.log('=== demo-resource - socketio - timeBeforeAllIdentities ===');
	console.log(timeBeforeAllIdentities);
	const allIdentities = await backendAPI.getAllIdentities(sessionId);
	const timeAfterAllIdentities = new Date();
	console.log('=== demo-resource - socketio - timeAfterAllIdentities ===');
	console.log(timeAfterAllIdentities);
	console.log('=== demo-resource - socketio - timeTaken ===');
	console.log(timeAfterAllIdentities.getTime() - timeBeforeSnapshotAndPolicies.getTime());
	payload.identities.push(...allIdentities);
	// one public identity:
	payload.identities.push({
		id: PUBLIC_IDENTITY_ID,
		name: 'All users',
		type: IdentityType.PUBLIC
	});

	return { payload };
};
