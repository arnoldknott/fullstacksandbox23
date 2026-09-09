import { error } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { MessageExtended, NumericalExtended } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const presentationPath = url.pathname.split('/presentation/')[1];
	console.log('=== 🧦 presentation - devF23 - INTENTION - presentationPath ===');
	console.log(presentationPath);
	const presentationResponse = await backendAPI.get(null, '/presentation/path/' + presentationPath);
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
	if (!questionIntentionId || !questionMotivationId || !questionCommentsId) {
		error(404, 'Required question ids were not provided');
	}
	const snapshotQuery = (parentId: string) =>
		'?parent-id=' +
		encodeURIComponent(parentId) +
		'&include=creation-date&sort=creation-date&direction=desc';
	const [intentionSnapshot, motivationSnapshot, commentsSnapshot] = await Promise.all([
		backendAPI.getSnapshot<MessageExtended>(
			null,
			'/quiz/message/snapshot' + snapshotQuery(questionIntentionId)
		),
		backendAPI.getSnapshot<NumericalExtended>(
			null,
			'/quiz/numerical/snapshot' + snapshotQuery(questionMotivationId)
		),
		backendAPI.getSnapshot<MessageExtended>(
			null,
			'/quiz/message/snapshot' + snapshotQuery(questionCommentsId)
		)
	]);
	return {
		questionsData: {
			intention: {
				id: questionIntentionId,
				messages: intentionSnapshot.entities,
				cursor: intentionSnapshot.cursor
			},
			motivation: {
				id: questionMotivationId,
				numericals: motivationSnapshot.entities,
				cursor: motivationSnapshot.cursor
			},
			comments: {
				id: questionCommentsId,
				messages: commentsSnapshot.entities,
				cursor: commentsSnapshot.cursor
			}
		}
	};
};
