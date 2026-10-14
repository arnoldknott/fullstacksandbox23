import { backendAPI } from '$lib/server/apis/backendApi';
import type { MessageExtended, Presentation, Question, QuestionExtended } from '$lib/types';

import type { PageServerLoad } from './$types';
import { presentationStatePrefix } from './inputs';

export const load: PageServerLoad = async ({ url, locals }) => {
	const presenterSessionId =
		url.searchParams.get('presenter') === 'true' && locals.sessionData?.loggedIn
			? locals.sessionData.sessionId
			: null;
	const presentationPath = url.pathname.split('/presentation/')[1];
	const presentationResponse = await backendAPI.get(null, '/presentation/path/' + presentationPath);
	const payload = {
		presentation: {} as Presentation,
		questions: [] as Question[],
		presenterStateSnapshot: { entities: [] as QuestionExtended[], cursor: 0 },
		// motivationSnapshot: { entities: [] as NumericalExtended[], cursor: 0 },
		namesSnapshot: { entities: [] as MessageExtended[], cursor: 0 },
		placesSnapshot: { entities: [] as MessageExtended[], cursor: 0 },
		booksSnapshot: { entities: [] as MessageExtended[], cursor: 0 },
		commentsSnapshot: { entities: [] as MessageExtended[], cursor: 0 },
		qualitativeFeedbackSnapshot: { entities: [] as MessageExtended[], cursor: 0 }
	};
	if (presentationResponse.status === 200) {
		const presentationData = (await presentationResponse.json()) as Presentation;
		payload.presentation = presentationData;
		payload.questions = presentationData.questions ?? [];
		const stateQuestion = payload.questions.find((question) =>
			question.question.startsWith(presentationStatePrefix)
		);
		// const motivationQuestion = payload.questions.find((question) =>
		// 	question.question.includes('motivation')
		// );
		const namesQuestion = payload.questions.find((question) => question.question === 'cbs-names');
		const placesQuestion = payload.questions.find((question) => question.question === 'cbs-places');
		const booksQuestion = payload.questions.find((question) => question.question === 'cbs-books');
		const commentsQuestion = payload.questions.find(
			(question) => question.question === 'cbs-comments'
		);
		const qualitativeFeedbackQuestion = payload.questions.find(
			(question) => question.question === 'cbs-qualitative-feedback'
		);
		// [payload.motivationSnapshot, payload.placesSnapshot, payload.commentsSnapshot] =
		[
			payload.presenterStateSnapshot,
			payload.namesSnapshot,
			payload.placesSnapshot,
			payload.booksSnapshot,
			payload.commentsSnapshot,
			payload.qualitativeFeedbackSnapshot
		] = await Promise.all([
			stateQuestion
				? backendAPI
						.getEntity<QuestionExtended>(presenterSessionId, `/quiz/question/${stateQuestion.id}`)
						.then(async (state) => {
							if (presenterSessionId) {
								const right = await backendAPI.get(
									presenterSessionId,
									`/access/right/resource/${stateQuestion.id}`
								);
								state.entity.access_right = right.ok ? await right.json() : undefined;
							}
							return { entities: [state.entity], cursor: state.cursor };
						})
				: Promise.resolve({ entities: [] as QuestionExtended[], cursor: 0 }),
			// motivationQuestion?.id
			// 	? backendAPI.getSnapshot<NumericalExtended>(
			// 			null,
			// 			`/quiz/numerical/snapshot?parent-id=${encodeURIComponent(motivationQuestion?.id)}`
			// 		)
			// 	: Promise.resolve({ entities: [] as NumericalExtended[], cursor: 0 }),
			namesQuestion?.id
				? backendAPI.getSnapshot<MessageExtended>(
						null,
						`/quiz/message/snapshot?parent-id=${encodeURIComponent(namesQuestion?.id)}&include=creation-date&sort=creation-date&direction=desc`
					)
				: Promise.resolve({ entities: [] as MessageExtended[], cursor: 0 }),
			placesQuestion?.id
				? backendAPI.getSnapshot<MessageExtended>(
						null,
						`/quiz/message/snapshot?parent-id=${encodeURIComponent(placesQuestion?.id)}&include=creation-date&sort=creation-date&direction=desc`
					)
				: Promise.resolve({ entities: [] as MessageExtended[], cursor: 0 }),
			booksQuestion?.id
				? backendAPI.getSnapshot<MessageExtended>(
						null,
						`/quiz/message/snapshot?parent-id=${encodeURIComponent(booksQuestion?.id)}&include=creation-date&sort=creation-date&direction=desc`
					)
				: Promise.resolve({ entities: [] as MessageExtended[], cursor: 0 }),
			commentsQuestion?.id
				? backendAPI.getSnapshot<MessageExtended>(
						null,
						`/quiz/message/snapshot?parent-id=${encodeURIComponent(commentsQuestion?.id)}&include=creation-date&sort=creation-date&direction=desc`
					)
				: Promise.resolve({ entities: [] as MessageExtended[], cursor: 0 }),
			qualitativeFeedbackQuestion?.id
				? backendAPI.getSnapshot<MessageExtended>(
						null,
						`/quiz/message/snapshot?parent-id=${encodeURIComponent(qualitativeFeedbackQuestion?.id)}&include=creation-date&sort=creation-date&direction=asc`
					)
				: Promise.resolve({ entities: [] as MessageExtended[], cursor: 0 })
		]);
	} else {
		// TBD: consider rising an error herem,
		// so client side can react accordingly and not show the relevant elements
		// error(404, 'presentationData could not be loaded');
		console.error(404, 'presentationData could not be loaded');
	}
	return { payload };
};
