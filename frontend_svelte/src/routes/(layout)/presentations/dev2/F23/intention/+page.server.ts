import type { PageServerLoad } from './$types';
import { backendAPI } from '$lib/server/apis/backendApi';
import { error } from '@sveltejs/kit';

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
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		error(404, 'questionsData.intention could not be loaded');
	}
	if (responseMotivation.status === 200) {
		const motivationData = await responseMotivation.json();
		if (questionsData) {
			questionsData.motivation = motivationData;
		} else {
			questionsData = { motivation: motivationData };
		}
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		error(404, 'questionsData.motivation could not be loaded');
	}
	console.log('=== questionsData in +page.server.ts === ');
	console.log(questionsData);
	return { questionsData };
};
