import { error } from '@sveltejs/kit';

import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type {
	Hierarchy,
	Identity,
	MessageExtended,
	NumericalExtended,
	QuestionExtended
} from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const questionId = params.id;
	const sessionId = locals.sessionData.sessionId;
	const snapshotQuery =
		'?parent-id=' +
		encodeURIComponent(questionId) +
		'&include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc';
	const [questionSnapshot, messageSnapshot, numericalSnapshot, hierarchiesResponse] =
		await Promise.all([
			backendAPI.getEntity<QuestionExtended>(sessionId, '/quiz/question/' + questionId),
			backendAPI.getSnapshot<MessageExtended>(sessionId, '/quiz/message/snapshot' + snapshotQuery),
			backendAPI.getSnapshot<NumericalExtended>(
				sessionId,
				'/quiz/numerical/snapshot' + snapshotQuery
			),
			backendAPI.get(sessionId, '/access/hierarchies?parent-id=' + encodeURIComponent(questionId))
		]);
	if (!hierarchiesResponse.ok) {
		error(502, 'Answer hierarchies could not be loaded');
	}

	const [policies, myTeamsIdentities, allIdentities] = await Promise.all([
		backendAPI.getAccessPolicies(sessionId, [
			questionId,
			...[...messageSnapshot.entities, ...numericalSnapshot.entities].map((answer) => answer.id)
		]),
		microsoftGraph.getAttachedTeamsAsIdentities(
			sessionId,
			locals.sessionData.currentUser?.azure_token_groups
		),
		backendAPI.getAllIdentities(sessionId)
	]);
	const hierarchies = (await hierarchiesResponse.json()) as Hierarchy[];
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	const hierarchiesByEntity = Object.groupBy(hierarchies, (hierarchy) => hierarchy.child_id);
	for (const answer of [...messageSnapshot.entities, ...numericalSnapshot.entities]) {
		answer.access_policies = policiesByEntity[answer.id] ?? [];
		answer.hierarchies = hierarchiesByEntity[answer.id] ?? [];
	}

	const question = questionSnapshot.entity;
	question.access_policies = policiesByEntity[questionId] ?? [];
	const identities: Identity[] = [
		...myTeamsIdentities,
		...allIdentities,
		{ id: PUBLIC_IDENTITY_ID, name: 'All users', type: IdentityType.PUBLIC }
	];

	return {
		questionsData: {
			questions: question,
			questionCursor: questionSnapshot.cursor,
			identities,
			messages: messageSnapshot.entities,
			messageCursor: messageSnapshot.cursor,
			numericals: numericalSnapshot.entities,
			numericalCursor: numericalSnapshot.cursor
		}
	};
};
