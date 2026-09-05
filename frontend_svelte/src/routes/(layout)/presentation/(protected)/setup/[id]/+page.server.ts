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
	const [presentationResponse, questionsResponse, policiesResponse, hierarchiesResponse] =
		await Promise.all([
			backendAPI.get(sessionId, '/presentation/' + presentationId),
			backendAPI.get(
				sessionId,
				'/quiz/question/snapshot?include=creation_date&include=last_modified_date&include=access_right&sort=creation_date&direction=desc'
			),
			backendAPI.get(sessionId, '/access/policy/resource/type/Question'),
			backendAPI.get(sessionId, '/access/hierarchies?parent_id=' + presentationId)
		]);
	if (presentationResponse.status === 200) {
		const presentationData = await presentationResponse.json();
		payload.presentation = presentationData;
	} else {
		console.error(404, 'presentationData could not be loaded');
	}
	if (!questionsResponse.ok) {
		error(questionsResponse.status, 'Questions could not be loaded');
	}
	if (!policiesResponse.ok) {
		error(policiesResponse.status, 'Question access policies could not be loaded');
	}
	if (!hierarchiesResponse.ok) {
		error(hierarchiesResponse.status, 'Question hierarchies could not be loaded');
	}
	const cursor = questionsResponse.headers.get('X-Entity-Cursor');
	if (cursor === null) {
		error(502, 'Question snapshot did not include a cursor');
	}
	const questions: QuestionExtended[] = await questionsResponse.json();
	const policies: AccessPolicy[] = await policiesResponse.json();
	const hierarchies: Hierarchy[] = await hierarchiesResponse.json();
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	const hierarchiesByEntity = Object.groupBy(hierarchies, (hierarchy) => hierarchy.child_id);
	for (const question of questions) {
		question.access_policies = policiesByEntity[question.id] ?? [];
		question.hierarchies = hierarchiesByEntity[question.id] ?? [];
	}
	payload.questions = questions;
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
