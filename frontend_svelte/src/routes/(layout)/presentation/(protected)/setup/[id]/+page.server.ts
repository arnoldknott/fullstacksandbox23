import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type {
	Hierarchy,
	Identity,
	NumberExtended,
	PresentationExtended,
	QuestionExtended,
	TextExtended
} from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const payload = {
		presentation: {} as PresentationExtended,
		presentationCursor: 0,
		questions: [] as QuestionExtended[],
		texts: [] as TextExtended[],
		textCursor: 0,
		numbers: [] as NumberExtended[],
		numberCursor: 0,
		cursor: 0,
		identities: [] as Identity[]
	};
	const presentationId = params.id;
	const snapshotQuery =
		'?include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc&parent-id=' +
		encodeURIComponent(presentationId);
	const [
		presentationSnapshot,
		questionSnapshot,
		textSnapshot,
		numberSnapshot,
		hierarchiesResponse
	] = await Promise.all([
		backendAPI.getEntity<PresentationExtended>(sessionId, '/presentation/' + presentationId),
		backendAPI.getSnapshot<QuestionExtended>(
			sessionId,
			'/quiz/question/snapshot?include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc&parent-id=' +
				encodeURIComponent(presentationId)
		),
		backendAPI.getSnapshot<TextExtended>(sessionId, '/text/snapshot' + snapshotQuery),
		backendAPI.getSnapshot<NumberExtended>(sessionId, '/number/snapshot' + snapshotQuery),
		backendAPI.get(sessionId, '/access/hierarchies?parent-id=' + encodeURIComponent(presentationId))
	]);
	const presentation = presentationSnapshot.entity;
	// Read access data after the presentation cursor is captured so replay covers concurrent changes.
	const childTexts = textSnapshot.entities;
	const childNumbers = numberSnapshot.entities;
	const [presentationPoliciesResponse, presentationRightResponse, policies] = await Promise.all([
		backendAPI.get(sessionId, '/access/policy/resource/' + presentationId),
		backendAPI.get(sessionId, '/access/right/resource/' + presentationId),
		backendAPI.getAccessPolicies(sessionId, [
			...questionSnapshot.entities.map((question) => question.id),
			...childTexts.map((text) => text.id),
			...childNumbers.map((number) => number.id)
		])
	]);
	if (!presentationPoliciesResponse.ok) {
		error(presentationPoliciesResponse.status, 'Presentation access policies could not be loaded');
	}
	if (!presentationRightResponse.ok) {
		error(presentationRightResponse.status, 'Presentation access right could not be loaded');
	}
	presentation.access_policies = await presentationPoliciesResponse.json();
	presentation.access_right = await presentationRightResponse.json();
	payload.presentation = presentation;
	payload.presentationCursor = presentationSnapshot.cursor;
	if (!hierarchiesResponse.ok) {
		error(hierarchiesResponse.status, 'Question hierarchies could not be loaded');
	}
	const questions = questionSnapshot.entities;
	const hierarchies: Hierarchy[] = await hierarchiesResponse.json();
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	const hierarchiesByEntity = Object.groupBy(hierarchies, (hierarchy) => hierarchy.child_id);
	for (const entity of [...questions, ...childTexts, ...childNumbers]) {
		entity.access_policies = policiesByEntity[entity.id] ?? [];
		entity.hierarchies = hierarchiesByEntity[entity.id] ?? [];
	}
	payload.questions = questions;
	payload.texts = childTexts;
	payload.textCursor = textSnapshot.cursor;
	payload.numbers = childNumbers;
	payload.numberCursor = numberSnapshot.cursor;
	payload.cursor = questionSnapshot.cursor;
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
