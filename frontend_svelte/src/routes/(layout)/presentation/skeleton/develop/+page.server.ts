import { backendAPI } from '$lib/server/apis/backendApi';
import type { MessageExtended, Presentation, Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const presentationPath = url.pathname.split('/presentation/')[1];
	const presentationResponse = await backendAPI.get(null, '/presentation/path/' + presentationPath);
	const payload = {
		presentation: {} as Presentation,
		questions: [] as Question[],
		mapSnapshot: { entities: [] as MessageExtended[], cursor: 0 }
	};
	if (presentationResponse.status === 200) {
		const presentationData = (await presentationResponse.json()) as Presentation;
		payload.presentation = presentationData;
		payload.questions = presentationData.questions ?? [];
		const mapQuestion = payload.questions.find((question) => question.question.includes('map'));
		if (mapQuestion) {
			const query =
				'?parent-id=' +
				encodeURIComponent(mapQuestion.id) +
				'&include=creation-date&sort=creation-date&direction=desc';
			payload.mapSnapshot = await backendAPI.getSnapshot<MessageExtended>(
				null,
				'/quiz/message/snapshot' + query
			);
		}
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		// error(404, 'presentationData could not be loaded');
		console.error(404, 'presentationData could not be loaded');
	}
	return { payload };
};
