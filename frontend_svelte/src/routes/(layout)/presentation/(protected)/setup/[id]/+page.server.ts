import { backendAPI } from '$lib/server/apis/backendApi';
import type { Presentation } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const payload = {
		presentation: {} as Presentation
	};
	const presentationId = url.pathname.split('/presentation/setup/')[1];
	console.log('=== 🧦 presentation - setup - presentationId ===');
	console.log(presentationId);
	const presentationResponse = await backendAPI.get(sessionId, '/presentation/' + presentationId);
	if (presentationResponse.status === 200) {
		const presentationData = await presentationResponse.json();
		payload.presentation = presentationData;
	} else {
		console.error(404, 'presentationData could not be loaded');
	}
	return { payload };
};
