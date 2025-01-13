import type { PageServerLoad } from './$types';
import { microsoftGraph, type MicrosoftTeamBasicInformation } from '$lib/server/apis';
// const getAllMicrosoftTeams = async (sessionId: string, azureGroups: string[]) => {

// }

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	// const myTeams: MicrosoftTeamBasicInformation[] = [];
	// if (locals.sessionData.userProfile) {
	// 	const myAzureGroups = locals.sessionData.userProfile.azure_token_groups;
	// 	if (myAzureGroups) {
	// 		await Promise.all(
	// 			myAzureGroups.map(async (azureGroup) => {
	// 				const response = await microsoftGraph.get(sessionId, `/teams/${azureGroup}`, [
	// 					'Team.ReadBasic.All'
	// 				]);
	// 				if (response.status === 200) {
	// 					const microsoftTeam = await response.json();
	// 					myTeams.push({
	// 						id: microsoftTeam.id,
	// 						displayName: microsoftTeam.displayName,
	// 						description: microsoftTeam.description
	// 					});
	// 				}
	// 			})
	// 		);
	// 	}
	// }

	// let myTeams: MicrosoftTeamBasicInformation[] = [];
	// if (locals.sessionData.userProfile) {
	// 	const myAzureGroupIds = locals.sessionData.userProfile.azure_token_groups;
	// 	if (myAzureGroupIds) {
	// 		myTeams = await microsoftGraph.getAttachedTeams(sessionId, myAzureGroupIds);
	// 	}
	// }

	let myTeams: MicrosoftTeamBasicInformation[] = [];
	if (locals.sessionData.userProfile && locals.sessionData.userProfile.azure_token_groups) {
		myTeams = await microsoftGraph.getAttachedTeams(
			sessionId,
			locals.sessionData.userProfile.azure_token_groups
		);
	}

	console.log(
		'=== src - routes - %28layout%29 - %28protected%29 - protected - identities - %2Bpage.server.ts - myTeams ==='
	);
	console.log(myTeams);

	return {
		microsoftTeams: myTeams
	};
};
