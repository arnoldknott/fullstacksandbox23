import { error } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const presentationPath = url.pathname.split('/presentation/')[1];
	console.log('=== 🧦 presentation - devF23 - INTENTION - presentationPath ===');
	console.log(presentationPath);
	const presentationResponse = await backendAPI.get(null, '/presentation/paths/' + presentationPath);
	if (presentationResponse.status === 200) {
		const presentationData = await presentationResponse.json();
		console.log('=== 🧦 presentation - devF23 - INTENTION - pre-loaded presentationData ===');
		console.log(presentationData);
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		// error(404, 'presentationData could not be loaded');
		console.error(404, 'presentationData could not be loaded');
	}

	// TBD: replace the id's from  query strings with the linked questions from the presentationResponse
	const questionIntentionId = url.searchParams.get('q-intention');
	const questionMotivationId = url.searchParams.get('q-motivation');
	const questionCommentsId = url.searchParams.get('q-comments');
	const responseIntention = await backendAPI.get(null, '/quiz/question/' + questionIntentionId);
	const responseMotivation = await backendAPI.get(null, '/quiz/question/' + questionMotivationId);
	const responseComments = await backendAPI.get(null, '/quiz/question/' + questionCommentsId);
	type QuestionData = {
		intention?: Question;
		motivation?: Question;
		comments?: Question;
	};
	let questionsData: QuestionData = {
		intention: undefined,
		motivation: undefined,
		comments: undefined
	};
	if (responseIntention.status === 200) {
		const intentionData = await responseIntention.json();
		questionsData = { intention: intentionData };
		// console.log('=== 🧦 presentation - devF23 - INTENTION - pre-loaded intentionData ===');
		// console.log(intentionData);
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
	if (responseComments.status === 200) {
		const commentsData = await responseComments.json();
		// console.log('=== 🧦 presentation - devF23 - COMMENTS - pre-loaded commentsData ===');
		// console.log(commentsData);
		if (questionsData) {
			questionsData.comments = commentsData;
		} else {
			questionsData = { comments: commentsData };
		}
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		error(404, 'questionsData.comments could not be loaded');
	}
	return { questionsData };
};
