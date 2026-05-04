import type { PageServerLoad } from './$types';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { Presentation } from '$lib/types';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const responsePresentations = await backendAPI.get(sessionId, '/presentation/');
	const payload = {
		presentations: [] as Presentation[]
	};
	if (responsePresentations.status === 200) {
		const presentationsData = await responsePresentations.json();
		payload.presentations = presentationsData;
	}
	return { payload };
};
