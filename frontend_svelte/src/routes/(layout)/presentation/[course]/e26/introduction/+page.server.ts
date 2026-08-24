

import { backendAPI } from '$lib/server/apis/backendApi';
import type { Presentation, Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const presentationPath = url.pathname.split('/presentation/')[1];
	const presentationResponse = await backendAPI.get(null, '/presentation/path/' + presentationPath);
	// let questionMotivationId: string = '';
	// let questionCommentsId: string = '';
    const payload = {
        presentation: {} as Presentation,
        questions: [] as Question[]
    };
	if (presentationResponse.status === 200) {
		const presentationData = await presentationResponse.json();
        payload.presentation = presentationData
		// console.log('=== 🧦 presentation - [course] - e26 ===');
		// console.log(presentationData);
		// questionMotivationId =
		// 	presentationData.questions
		// 		.map((q: { id: string }) => q.id)
		// 		.find((id: string) => id.includes('motivation')) || '';
		// questionCommentsId =
		// 	presentationData.questions
		// 		.map((q: { id: string }) => q.id)
		// 		.find((id: string) => id.includes('comments')) || '';
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		// error(404, 'presentationData could not be loaded');
		console.error(404, 'presentationData could not be loaded');
	}
	// const responseIntention = await backendAPI.get(
	// 	null,
	// 	'/quiz/question/' + questionIntentionId
	// );
	// const responseMotivation = await backendAPI.get(null, '/quiz/question/' + questionMotivationId);
	// const responseComments = await backendAPI.get(null, '/quiz/question/' + questionCommentsId);
	// type QuestionData = {
	// 	// intention?: Question;
	// 	motivation?: Question;
	// 	comments?: Question;
	// };
	// let questionsData: QuestionData = {
	// 	// intention: undefined,
	// 	motivation: undefined,
	// 	comments: undefined
	// };
	// if (responseIntention.status === 200) {
	// 	const intentionData = await responseIntention.json();
	// 	questionsData = { intention: intentionData };
	// 	// console.log('=== 🧦 presentation - devF23 - INTENTION - pre-loaded intentionData ===');
	// 	// console.log(intentionData);
	// } else {
	// 	// TBD: consider rising an error herem,
	// 	// so client side can react accordingly and not show the relevant elements
	// 	error(404, 'questionsData.intention could not be loaded');
	// }
	// if (responseMotivation.status === 200) {
	// 	const motivationData = await responseMotivation.json();
	// 	if (questionsData) {
	// 		questionsData.motivation = motivationData;
	// 	} else {
	// 		questionsData = { motivation: motivationData };
	// 	}
	// } else {
	// 	// TBD: consider rising an error herem,
	// 	// so client side can react accordingly and not show the relevant elements
	// 	error(404, 'questionsData.motivation could not be loaded');
	// }
	// if (responseComments.status === 200) {
	// 	const commentsData = await responseComments.json();
	// 	// console.log('=== 🧦 presentation - devF23 - COMMENTS - pre-loaded commentsData ===');
	// 	// console.log(commentsData);
	// 	if (questionsData) {
	// 		questionsData.comments = commentsData;
	// 	} else {
	// 		questionsData = { comments: commentsData };
	// 	}
	// } else {
	// 	// TBD: consider rising an error herem,
	// 	// so client side can react accordingly and not show the relevant elements
	// 	error(404, 'questionsData.comments could not be loaded');
	// }
	return { payload };
};
