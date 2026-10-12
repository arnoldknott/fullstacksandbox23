import { error } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { Hierarchy, MessageExtended, NumericalExtended, Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const questionId = params.id;
	const sessionId = locals.sessionData.sessionId;
	const snapshotQuery =
		'?parent-id=' +
		encodeURIComponent(questionId) +
		'&include=creation-date&include=last-modified-date&include=access-right&sort=creation-date&direction=desc';
	const [questionResponse, messageSnapshot, numericalSnapshot, hierarchiesResponse] =
		await Promise.all([
			backendAPI.get(sessionId, '/quiz/question/' + questionId),
			backendAPI.getSnapshot<MessageExtended>(sessionId, '/quiz/message/snapshot' + snapshotQuery),
			backendAPI.getSnapshot<NumericalExtended>(
				sessionId,
				'/quiz/numerical/snapshot' + snapshotQuery
			),
			backendAPI.get(sessionId, '/access/hierarchies?parent-id=' + encodeURIComponent(questionId))
		]);
	if (!questionResponse.ok) {
		error(questionResponse.status, 'Question could not be loaded');
	}
	if (!hierarchiesResponse.ok) {
		error(502, 'Answer hierarchies could not be loaded');
	}

	const policies = await backendAPI.getAccessPolicies(
		sessionId,
		[...messageSnapshot.entities, ...numericalSnapshot.entities].map((answer) => answer.id)
	);
	const hierarchies = (await hierarchiesResponse.json()) as Hierarchy[];
	const policiesByEntity = Object.groupBy(policies, (policy) => policy.resource_id);
	const hierarchiesByEntity = Object.groupBy(hierarchies, (hierarchy) => hierarchy.child_id);
	for (const answer of [...messageSnapshot.entities, ...numericalSnapshot.entities]) {
		answer.access_policies = policiesByEntity[answer.id] ?? [];
		answer.hierarchies = hierarchiesByEntity[answer.id] ?? [];
	}

	return {
		questionsData: {
			questions: (await questionResponse.json()) as Question,
			messages: messageSnapshot.entities,
			messageCursor: messageSnapshot.cursor,
			numericals: numericalSnapshot.entities,
			numericalCursor: numericalSnapshot.cursor
		}
	};
};
