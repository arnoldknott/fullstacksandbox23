import type { PageServerLoad } from './$types';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { MicrosoftTeamBasic } from '$lib/types';

export const load: PageServerLoad = async ({ locals }) => {
    const sessionId = locals.sessionData.sessionId;

    let myTeams: MicrosoftTeamBasic[] = [];
    if (locals.sessionData.userProfile && locals.sessionData.userProfile.azure_token_groups) {
        myTeams = await microsoftGraph.getAttachedTeams(
            sessionId,
            locals.sessionData.userProfile.azure_token_groups
        );
    }

    return {
        microsoftTeams: myTeams
    };
};
