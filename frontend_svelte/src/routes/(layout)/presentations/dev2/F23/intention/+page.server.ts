import type { PageServerLoad } from './$types';

import { backendAPI } from '$lib/server/apis/backendApi';

export const load: PageServerLoad = async ({ url }) => {
	const questionIntentionId = url.searchParams.get('q-intention');
	const questionMotivationId = url.searchParams.get('q-motivation');
	const responseIntention = await backendAPI.get(
		null,
		'/quiz/question/public/' + questionIntentionId
	);
	const responseMotivation = await backendAPI.get(
		null,
		'/quiz/question/public/' + questionMotivationId
	);
	let questionsData = null;
	if (responseIntention.status === 200) {
		const intentionData = await responseIntention.json();
		questionsData = { intention: intentionData };
	}
	if (responseMotivation.status === 200) {
		const motivationData = await responseMotivation.json();
		if (questionsData) {
			questionsData.motivation = motivationData;
		} else {
			questionsData = { motivation: motivationData };
		}
	}
	return { questionsData };
};
