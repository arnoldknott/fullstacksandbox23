import { IdentityType, PUBLIC_IDENTITY_ID } from '$lib/accessHandler';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { Identity, Presentation, Question } from '$lib/types';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const payload = {
		presentation: {} as Presentation,
		questions: [] as Question[],
		identities: [] as Identity[]
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
	// add all accessable questions:
	const questionsResponse = await backendAPI.get(sessionId, '/quiz/question/');
	if (questionsResponse.status === 200) {
		const questionsData = await questionsResponse.json();
		payload.questions = questionsData;
	} else {
		console.error(404, 'questionsData could not be loaded');
	}
	// add all linked Microsoft Teams identities:
	const myTeamsIdentities = await microsoftGraph.getAttachedTeamsAsIdentities(
		sessionId,
		locals.sessionData.currentUser?.azure_token_groups
	);
	payload.identities.push(...myTeamsIdentities);
	// add all app internal identities (users, ueber-groups, groups, sub-groups, sub-sub-groups):
	const allIdentities = await backendAPI.getAllIdentities(sessionId);
	payload.identities.push(...allIdentities);
	// add one public identity:
	payload.identities.push({
		id: PUBLIC_IDENTITY_ID,
		name: 'All users',
		type: IdentityType.PUBLIC
	});
	return { payload };
};
