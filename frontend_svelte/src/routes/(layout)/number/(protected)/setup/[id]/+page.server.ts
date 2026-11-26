import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { Hierarchy, Identity, NumberExtended, TextExtended } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const numberId = params.id;
	const sessionId = locals.sessionData.sessionId;
	const snapshotQuery =
		'?parent-id=' +
		encodeURIComponent(numberId) +
		'&include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc';
	const [numberSnapshot, textsSnapshot, childNumbersSnapshot, hierarchiesResponse] =
		await Promise.all([
			backendAPI.getEntity<NumberExtended>(sessionId, '/number/' + numberId),
			backendAPI.getSnapshot<TextExtended>(sessionId, '/text/snapshot' + snapshotQuery),
			backendAPI.getSnapshot<NumberExtended>(sessionId, '/number/snapshot' + snapshotQuery),
			backendAPI.get(sessionId, '/access/hierarchies?parent-id=' + encodeURIComponent(numberId))
		]);
	if (!hierarchiesResponse.ok) {
		error(hierarchiesResponse.status, 'Number child hierarchies could not be loaded');
	}

	const texts = textsSnapshot.entities;
	const childNumbers = childNumbersSnapshot.entities;
	const [policies, myTeamsIdentities, allIdentities] = await Promise.all([
		backendAPI.getAccessPolicies(sessionId, [
			numberId,
			...[...texts, ...childNumbers].map((entity) => entity.id)
		]),
		microsoftGraph.getAttachedTeamsAsIdentities(
			sessionId,
			locals.sessionData.currentUser?.azure_token_groups
		),
		backendAPI.getAllIdentities(sessionId)
	]);
	const hierarchies: Hierarchy[] = await hierarchiesResponse.json();
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	const hierarchiesByEntity = Object.groupBy(hierarchies, (hierarchy) => hierarchy.child_id);
	for (const entity of [...texts, ...childNumbers]) {
		entity.access_policies = policiesByEntity[entity.id] ?? [];
		entity.hierarchies = hierarchiesByEntity[entity.id] ?? [];
	}
	const number = numberSnapshot.entity;
	number.access_policies = policiesByEntity[numberId] ?? [];
	number.hierarchies = hierarchiesByEntity[numberId] ?? [];

	const identities: Identity[] = [
		...myTeamsIdentities,
		...allIdentities,
		{ id: PUBLIC_IDENTITY_ID, name: 'All users', type: IdentityType.PUBLIC }
	];
	return {
		payload: {
			number,
			numberCursor: numberSnapshot.cursor,
			texts,
			textsCursor: textsSnapshot.cursor,
			numbers: childNumbers,
			numbersCursor: childNumbersSnapshot.cursor,
			identities
		}
	};
};
