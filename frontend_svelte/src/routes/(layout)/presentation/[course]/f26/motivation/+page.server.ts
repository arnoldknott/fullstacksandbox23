import { error } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { MessageExtended, NumericalExtended } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const questionMotivationId = url.searchParams.get('q-motivation');
	const questionCommentsId = url.searchParams.get('q-comments');
	if (!questionMotivationId || !questionCommentsId) {
		error(404, 'Required question ids were not provided');
	}
	const snapshotQuery = (parentId: string) =>
		'?parent-id=' +
		encodeURIComponent(parentId) +
		'&include=creation-date&sort=creation-date&direction=desc';
	const [motivationSnapshot, commentsSnapshot] = await Promise.all([
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
