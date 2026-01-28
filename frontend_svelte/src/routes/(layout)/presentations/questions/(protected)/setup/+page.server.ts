import type { PageServerLoad } from './$types';

import { backendAPI } from '$lib/server/apis/backendApi';

export const load: PageServerLoad = async ({ url }) => {
	const questionId = url.searchParams.get('question-id');
	const response = await backendAPI.get(null, '/quiz/question/public/' + questionId);
	let questionsData = null;
	if (response.status === 200) {
		const questionData = await response.json();
		questionsData = { questions: questionData };
	}
	return { questionsData };
};
