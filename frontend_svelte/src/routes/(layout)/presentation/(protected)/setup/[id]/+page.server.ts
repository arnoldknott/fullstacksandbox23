import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type {
	AccessPolicy,
	Hierarchy,
	Identity,
	PresentationExtended,
	QuestionExtended
} from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const payload = {
		presentation: {} as PresentationExtended,
		presentationCursor: 0,
		questions: [] as QuestionExtended[],
		cursor: 0,
		identities: [] as Identity[]
	};
	const presentationId = params.id;
	const [presentationResponse, questionSnapshot, policiesResponse, hierarchiesResponse] =
		await Promise.all([
			backendAPI.get(sessionId, '/presentation/' + presentationId),
			backendAPI.getSnapshot<QuestionExtended>(
				sessionId,
				'/quiz/question/snapshot?include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc&parent-id=' +
					presentationId
			),
			backendAPI.get(sessionId, '/access/policy/resource/type/Question'),
			backendAPI.get(sessionId, '/access/hierarchies?parent-id=' + presentationId)
		]);
	if (!presentationResponse.ok) {
		error(presentationResponse.status, 'Presentation could not be loaded');
	}
	const rawCursor = presentationResponse.headers.get('X-Entity-Cursor');
	if (rawCursor === null) error(502, 'Presentation did not include a cursor');
	const presentationCursor = Number(rawCursor);
	if (!Number.isSafeInteger(presentationCursor) || presentationCursor < 0) {
		error(502, 'Presentation included an invalid cursor');
	}
	const presentation: PresentationExtended = await presentationResponse.json();
	// Read access data after the presentation cursor is captured so replay covers concurrent changes.
	const [presentationPoliciesResponse, presentationRightResponse] = await Promise.all([
		backendAPI.get(sessionId, '/access/policy/resource/' + presentationId),
		backendAPI.get(sessionId, '/access/right/resource/' + presentationId)
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
	payload.presentationCursor = presentationCursor;
	if (!policiesResponse.ok) {
		error(policiesResponse.status, 'Question access policies could not be loaded');
	}
	if (!hierarchiesResponse.ok) {
		error(hierarchiesResponse.status, 'Question hierarchies could not be loaded');
	}
	const questions = questionSnapshot.entities;
	const policies: AccessPolicy[] = await policiesResponse.json();
	const hierarchies: Hierarchy[] = await hierarchiesResponse.json();
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	const hierarchiesByEntity = Object.groupBy(hierarchies, (hierarchy) => hierarchy.child_id);
	for (const question of questions) {
		question.access_policies = policiesByEntity[question.id] ?? [];
		question.hierarchies = hierarchiesByEntity[question.id] ?? [];
	}
	payload.questions = questions;
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
