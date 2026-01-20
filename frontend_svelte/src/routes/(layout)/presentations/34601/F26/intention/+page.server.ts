import type { PageServerLoad } from './$types';

import { backendAPI } from '$lib/server/apis/backendApi';

export const load: PageServerLoad = async ({ url }) => {
	console.log(
		'=== routes - presentations - F26 - intention - page.server - load function executed ==='
	);
	console.log(url.searchParams.get('q-intention'));
	const questionIntentionId = url.searchParams.get('q-intention');
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
