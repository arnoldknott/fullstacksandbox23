import type { PageServerLoad } from './$types';
import { microsoftGraph } from '$lib/server/apis';

// const getAllMicrosoftTeams = async (sessionId: string, azureGroups: string[]) => {

// }

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;

	// const responseMe = await backendAPI.get(sessionId, '/user/me');
	// const me = await responseMe.json();
	let myTeams;
	if (locals.sessionData.userProfile) {
		const myAzureGroups = locals.sessionData.userProfile.azure_token_groups;
		myTeams =  myAzureGroups?.forEach(async (azureGroup) => {
			try {
                console.log('=== src - routes - %28layout%29 - %28protected%29 - protected - identities - %2Bpage.server.ts - azureGroup ===');
                console.log(azureGroup);
				const response = await microsoftGraph.get(sessionId, `/teams/${azureGroup}`, ["Team.ReadBasic.All"]);
				const microsoftTeam = await response.json();
                console.log('=== src - routes - %28layout%29 - %28protected%29 - protected - identities - %2Bpage.server.ts - microsoftTeam ===');
                console.log(microsoftTeam);
				return microsoftTeam;
			} catch {
				// the azure group is not a microsoft Teams team - ignore
				return;
			}
		});
	}

    console.log('=== src - routes - %28layout%29 - %28protected%29 - protected - identities - %2Bpage.server.ts - myTeams ===');
    console.log(myTeams);

	return {
		microsoftTeams: myTeams
	};
};
