import type { PageServerLoad } from './$types';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { Team as MicrosoftTeam } from '@microsoft/microsoft-graph-types';

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;

	let myTeams: MicrosoftTeam[] = [];
	// TBD: session is long-lived - needs to update more frequently
	if (locals.sessionData.currentUser && locals.sessionData.currentUser.azure_token_groups) {
		myTeams = await microsoftGraph.getAttachedTeams(
			sessionId,
			locals.sessionData.currentUser.azure_token_groups
		);
	}

	return {
		microsoftTeams: myTeams
	};
};
