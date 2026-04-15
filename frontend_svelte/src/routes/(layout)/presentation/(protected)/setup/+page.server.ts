import type { PageServerLoad } from './$types';

import { backendAPI } from '$lib/server/apis/backendApi';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const responseQuestions = await backendAPI.get(sessionId, '/quiz/question/');
	if (responseQuestions.status === 200) {
		const questionsData = await responseQuestions.json();
		return { questionsData: questionsData };
	} else {
		return { questionsData: [] };
	}
};
