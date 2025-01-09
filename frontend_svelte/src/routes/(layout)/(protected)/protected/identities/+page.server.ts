import type { PageServerLoad } from './$types';
import { microsoftGraph } from '$lib/server/apis';

// const getAllMicrosoftTeams = async (sessionId: string, azureGroups: string[]) => {

// }

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;

	// const responseMe = await backendAPI.get(sessionId, '/user/me');
	// const me = await responseMe.json();
    interface MicrosoftTeamBasicInformation {
        id: string;
        displayName: string;
        description: string;
    }

    let myTeams: MicrosoftTeamBasicInformation[] = [];
	if (locals.sessionData.userProfile) {
		const myAzureGroups = locals.sessionData.userProfile.azure_token_groups;
		if (myAzureGroups) {
			await Promise.all(myAzureGroups.map(async (azureGroup) => {
                const response = await microsoftGraph.get(sessionId, `/teams/${azureGroup}`, ["Team.ReadBasic.All"]);
                console.log('=== src - routes - %28layout%29 - %28protected%29 - protected - identities - %2Bpage.server.ts - response.status ===');
                console.log(response.status);
                if (response.status === 200) {
                    const microsoftTeam = await response.json();
                    myTeams.push({id: microsoftTeam.id, displayName: microsoftTeam.displayName, description: microsoftTeam.description});
                }
			}));
		}
	}

    console.log('=== src - routes - %28layout%29 - %28protected%29 - protected - identities - %2Bpage.server.ts - myTeams ===');
    console.log(myTeams);

	return {
		microsoftTeams: myTeams
	};
};
