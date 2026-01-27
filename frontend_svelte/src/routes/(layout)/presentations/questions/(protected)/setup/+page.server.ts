import type { PageServerLoad } from './$types';

import { backendAPI } from '$lib/server/apis/backendApi';

export const load: PageServerLoad = async ({ url }) => {
	const questionIntentionId = url.searchParams.get('question-id');
	const responseIntention = await backendAPI.get(
		null,
		'/quiz/question/public/' + questionIntentionId
	);
	let questionsData = null;
	if (responseIntention.status === 200) {
		const intentionData = await responseIntention.json();
		questionsData = { intention: intentionData };
	}
	return { questionsData };
};
