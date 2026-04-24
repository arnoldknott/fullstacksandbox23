import type { PageServerLoad } from './$types';

import { backendAPI } from '$lib/server/apis/backendApi';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const responsePresentations = await backendAPI.get(sessionId, '/presentation/');
	if (responsePresentations.status === 200) {
		const presentationsData = await responsePresentations.json();
		return { presentationsData: presentationsData };
	} else {
		return { presentationsData: [] };
	}
};
