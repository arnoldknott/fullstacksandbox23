import { error } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { MessageExtended, Presentation, QuestionExtended } from '$lib/types';

import { inputOptions, presentationStatePrefix } from '../inputs';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const presentationUrl = url.pathname.replace(/\/inputs\/?$/, '');
	const presentationPath = presentationUrl.split('/presentation/')[1];
	const response = await backendAPI.get(null, '/presentation/path/' + presentationPath);
	if (!response.ok) error(response.status, 'Presentation could not be loaded');
	const presentation = (await response.json()) as Presentation;
	const questions = presentation.questions ?? [];
	const stateQuestion = questions.find((question) =>
		question.question.startsWith(presentationStatePrefix)
	);
	const state = stateQuestion
		? await backendAPI.getEntity<QuestionExtended>(null, `/quiz/question/${stateQuestion.id}`)
		: undefined;
	const commentsQuestion = questions.find((question) => question.question.includes('comments'));
	const commentsSnapshot = commentsQuestion?.id
		? await backendAPI.getSnapshot<MessageExtended>(
				null,
				`/quiz/message/snapshot?parent-id=${encodeURIComponent(commentsQuestion?.id)}&include=creation-date&sort=creation-date&direction=desc`
			)
		: { entities: [] as MessageExtended[], cursor: 0 };
	return {
		presentationUrl,
		inputQuestions: Object.fromEntries(
			inputOptions.map((option) => [
				option.question,
				questions.find((question) => question.question === option.question)?.id
			])
		),
		stateSnapshot: { entities: state ? [state.entity] : [], cursor: state?.cursor ?? 0 },
		commentsSnapshot: commentsSnapshot
	};
};
