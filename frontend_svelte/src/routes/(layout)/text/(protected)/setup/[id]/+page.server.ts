import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { Hierarchy, Identity, NumberExtended, TextExtended } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const textId = params.id;
	const sessionId = locals.sessionData.sessionId;
	const snapshotQuery =
		'?parent-id=' +
		encodeURIComponent(textId) +
		'&include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc';
	const [textSnapshot, childTextsSnapshot, numbersSnapshot, hierarchiesResponse] =
		await Promise.all([
			backendAPI.getEntity<TextExtended>(sessionId, '/text/' + textId),
			backendAPI.getSnapshot<TextExtended>(sessionId, '/text/snapshot' + snapshotQuery),
			backendAPI.getSnapshot<NumberExtended>(sessionId, '/number/snapshot' + snapshotQuery),
			backendAPI.get(sessionId, '/access/hierarchies?parent-id=' + encodeURIComponent(textId))
		]);
	if (!hierarchiesResponse.ok) {
		error(hierarchiesResponse.status, 'Text child hierarchies could not be loaded');
	}

	const childTexts = childTextsSnapshot.entities;
	const numbers = numbersSnapshot.entities;
	const [policies, myTeamsIdentities, allIdentities] = await Promise.all([
		backendAPI.getAccessPolicies(sessionId, [
			textId,
			...[...childTexts, ...numbers].map((entity) => entity.id)
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
	for (const entity of [...childTexts, ...numbers]) {
		entity.access_policies = policiesByEntity[entity.id] ?? [];
		entity.hierarchies = hierarchiesByEntity[entity.id] ?? [];
	}
	const text = textSnapshot.entity;
	text.access_policies = policiesByEntity[textId] ?? [];
	text.hierarchies = hierarchiesByEntity[textId] ?? [];

	const identities: Identity[] = [
		...myTeamsIdentities,
		...allIdentities,
		{ id: PUBLIC_IDENTITY_ID, name: 'All users', type: IdentityType.PUBLIC }
	];
	return {
		payload: {
			text,
			textCursor: textSnapshot.cursor,
			texts: childTexts,
			textsCursor: childTextsSnapshot.cursor,
			numbers,
			numbersCursor: numbersSnapshot.cursor,
			identities
		}
	};
};
