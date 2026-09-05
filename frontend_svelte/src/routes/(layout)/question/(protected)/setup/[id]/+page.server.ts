import { error } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { MessageExtended, NumericalExtended, Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const questionId = params.id;
	const sessionId = locals.sessionData.sessionId;
	const snapshotQuery =
		'?parent_id=' +
		encodeURIComponent(questionId) +
		'&include=creation_date&sort=creation_date&direction=desc';
	const [questionResponse, messagesResponse, numericalsResponse] = await Promise.all([
		backendAPI.get(sessionId, '/quiz/question/' + questionId),
		backendAPI.get(sessionId, '/quiz/message/snapshot' + snapshotQuery),
		backendAPI.get(sessionId, '/quiz/numerical/snapshot' + snapshotQuery)
	]);
	if (!questionResponse.ok) {
		error(questionResponse.status, 'Question could not be loaded');
	}
	if (!messagesResponse.ok || !numericalsResponse.ok) {
		error(502, 'Question answers could not be loaded');
	}
	const messageCursor = messagesResponse.headers.get('X-Entity-Cursor');
	const numericalCursor = numericalsResponse.headers.get('X-Entity-Cursor');
	if (messageCursor === null || numericalCursor === null) {
		error(502, 'Question answer snapshot did not include a cursor');
	}
	return {
		questionsData: {
			questions: (await questionResponse.json()) as Question,
			messages: (await messagesResponse.json()) as MessageExtended[],
			messageCursor: Number.parseInt(messageCursor, 10),
			numericals: (await numericalsResponse.json()) as NumericalExtended[],
			numericalCursor: Number.parseInt(numericalCursor, 10)
		}
	};
};
