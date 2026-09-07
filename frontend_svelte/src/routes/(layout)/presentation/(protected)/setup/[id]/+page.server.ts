import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { AccessPolicy, Hierarchy, Identity, Presentation, QuestionExtended } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const payload = {
		presentation: {} as Presentation,
		questions: [] as QuestionExtended[],
		cursor: 0,
		identities: [] as Identity[]
	};
	const presentationId = url.pathname.split('/presentation/setup/')[1];
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
	if (presentationResponse.status === 200) {
		const presentationData = await presentationResponse.json();
		payload.presentation = presentationData;
	} else {
		console.error(404, 'presentationData could not be loaded');
	}
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
