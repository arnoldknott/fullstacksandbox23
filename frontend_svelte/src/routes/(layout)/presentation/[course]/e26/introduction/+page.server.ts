import { backendAPI } from '$lib/server/apis/backendApi';
import type { Presentation, Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const presentationPath = url.pathname.split('/presentation/')[1];
	const presentationResponse = await backendAPI.get(null, '/presentation/path/' + presentationPath);
	// const presentationResponse = await backendAPI.get(null, '/presentation/' + '2713ce81-c6da-4c64-b63b-66abca6c1c1e');
	const payload = {
		presentation: {} as Presentation,
		questions: [] as Question[]
	};
	if (presentationResponse.status === 200) {
		const presentationData = await presentationResponse.json();
		payload.presentation = presentationData;
		for (const question of presentationData.questions) {
			const questionResponse = await backendAPI.get(null, '/quiz/question/' + question.id);
			if (questionResponse.status === 200) {
				const questionData = await questionResponse.json();
				payload.questions.push(questionData);
			} else {
				console.warn(
					questionResponse.status,
					'questionData could not be loaded for question id: ' + question.id
				);
			}
		}
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		// error(404, 'presentationData could not be loaded');
		console.error(404, 'presentationData could not be loaded');
	}
	return { payload };
};
