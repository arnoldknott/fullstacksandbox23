import { backendAPI } from '$lib/server/apis/backendApi';
import type { MessageExtended, NumericalExtended, Presentation, Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const presentationPath = url.pathname.split('/presentation/')[1];
	const timeBeforePresentation = new Date();
	console.log('=== presentation - introduction - timeBeforePresentation ===');
	console.log(timeBeforePresentation);
	const presentationResponse = await backendAPI.get(null, '/presentation/path/' + presentationPath);
	const timeAfterPresentation = new Date();
	console.log('=== presentation - introduction - timeAfterPresentation ===');
	console.log(timeAfterPresentation);
	const payload = {
		presentation: {} as Presentation,
		questions: [] as Question[],
		motivationSnapshot: { entities: [] as NumericalExtended[], cursor: 0 },
		placesSnapshot: { entities: [] as MessageExtended[], cursor: 0 },
		commentsSnapshot: { entities: [] as MessageExtended[], cursor: 0 }
	};
	if (presentationResponse.status === 200) {
		const presentationData = (await presentationResponse.json()) as Presentation;
		payload.presentation = presentationData;
		payload.questions = presentationData.questions ?? [];
		const motivationQuestion = payload.questions.find((question) =>
			question.question.includes('motivation')
		);
		const placesQuestion = payload.questions.find((question) =>
			question.question.includes('places')
		);
		const commentsQuestion = payload.questions.find((question) =>
			question.question.includes('comments')
		);
		const timeBeforeAnswerSnapshots = new Date();
		console.log('=== presentation - introduction - timeBeforeAnswerSnapshots ===');
		console.log(timeBeforeAnswerSnapshots);
		[payload.motivationSnapshot, payload.placesSnapshot, payload.commentsSnapshot] =
			await Promise.all([
				motivationQuestion?.id
					? backendAPI.getSnapshot<NumericalExtended>(
							null,
							`/quiz/numerical/snapshot?parent-id=${encodeURIComponent(motivationQuestion?.id)}`
						)
					: Promise.resolve({ entities: [] as NumericalExtended[], cursor: 0 }),
				placesQuestion?.id
					? backendAPI.getSnapshot<MessageExtended>(
							null,
							`/quiz/message/snapshot?parent-id=${encodeURIComponent(placesQuestion?.id)}&include=creation-date&sort=creation-date&direction=desc`
						)
					: Promise.resolve({ entities: [] as MessageExtended[], cursor: 0 }),
				commentsQuestion?.id
					? backendAPI.getSnapshot<MessageExtended>(
							null,
							`/quiz/message/snapshot?parent-id=${encodeURIComponent(commentsQuestion?.id)}&include=creation-date&sort=creation-date&direction=desc`
						)
					: Promise.resolve({ entities: [] as MessageExtended[], cursor: 0 })
			]);
		const timeAfterAnswerSnapshots = new Date();
		console.log('=== presentation - introduction - timeAfterAnswerSnapshots ===');
		console.log(timeAfterAnswerSnapshots);
		const timeAfterPresentation = new Date();
		console.log("=== presentation - introduction - timeAfterPresentation ===");
		console.log(timeAfterPresentation);
		console.log("=== presentation - introduction - timeTaken ===");
		console.log(timeBeforePresentation.getTime() - timeBeforeAnswerSnapshots.getTime());
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		// error(404, 'presentationData could not be loaded');
		console.error(404, 'presentationData could not be loaded');
	}
	return { payload };
};
