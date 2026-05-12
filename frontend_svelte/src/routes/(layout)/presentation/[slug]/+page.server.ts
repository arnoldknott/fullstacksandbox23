import type { PageServerLoad } from './$types';

import { backendAPI } from '$lib/server/apis/backendApi';
import type { Presentation } from '$lib/types';

export const load: PageServerLoad = async ({ params, locals }) => {
	const sessionId = locals.sessionData.sessionId;
	// The [slug] can either be a user-defined slug or the uuid of the presenation
	// Check for user-defined slug first, which makes it easier human readable and shareable,
	// and then fallback to uuid if not found
	const presentationSlug = params.slug;

	const payload = {
		presentation: null as Presentation | null
	};
	const slugResponse = await backendAPI.get(sessionId, `/presentation/${presentationSlug}`);
	if (slugResponse.status === 200) {
		const presentationData = await slugResponse.json();
		payload.presentation = presentationData;
	} else {
		const uuidResponse = await backendAPI.get(sessionId, `/presentation/${presentationSlug}`);
		if (uuidResponse.status === 200) {
			const presentationData = await uuidResponse.json();
			payload.presentation = presentationData;
		}
	}
	return { payload };
};
