import { error } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { MessageExtended, NumericalExtended, Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const questionId = params.id;
	const sessionId = locals.sessionData.sessionId;
	const snapshotQuery =
		'?parent-id=' +
		encodeURIComponent(questionId) +
		'&include=creation-date&sort=creation-date&direction=desc';
	const [questionResponse, messageSnapshot, numericalSnapshot] = await Promise.all([
		backendAPI.get(sessionId, '/quiz/question/' + questionId),
		backendAPI.getSnapshot<MessageExtended>(sessionId, '/quiz/message/snapshot' + snapshotQuery),
		backendAPI.getSnapshot<NumericalExtended>(sessionId, '/quiz/numerical/snapshot' + snapshotQuery)
	]);
	if (!questionResponse.ok) {
		error(questionResponse.status, 'Question could not be loaded');
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
