import type { PageServerLoad } from './$types';
import { microsoftGraph } from '$lib/server/apis/msgraph';
// import type { MicrosoftTeamBasic } from '$lib/types';
import type { Team as MicrosoftTeam } from '@microsoft/microsoft-graph-types';
import type { UeberGroup } from '$lib/types';
import { backendAPI } from '$lib/server/apis/backendApi';
// const getAllMicrosoftTeams = async (sessionId: string, azureGroups: string[]) => {

// }

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	// const myTeams: MicrosoftTeamBasic[] = [];
	// if (locals.sessionData.currentUser) {
	// 	const myAzureGroups = locals.sessionData.currentUser.azure_token_groups;
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

	// let myTeams: MicrosoftTeamBasic[] = [];
	// if (locals.sessionData.currentUser) {
	// 	const myAzureGroupIds = locals.sessionData.currentUser.azure_token_groups;
	// 	if (myAzureGroupIds) {
	// 		myTeams = await microsoftGraph.getAttachedTeams(sessionId, myAzureGroupIds);
	// 	}
	// }

	let myTeams: MicrosoftTeam[] = [];
	// let mySecurityGroups: any[] = [];
	if (locals.sessionData.currentUser && locals.sessionData.currentUser.azure_token_groups) {
		myTeams = await microsoftGraph.getAttachedTeams(
			sessionId,
			locals.sessionData.currentUser.azure_token_groups
		);
		// mySecurityGroups = await microsoftGraph.getAttachedSecuriyGroups(
		// 	sessionId,
		// 	locals.sessionData.currentUser.azure_token_groups
		// )
		// const response = await microsoftGraph.get(sessionId, `/me/memberOf/?$filter=id in ('${locals.sessionData.currentUser.azure_token_groups.join("','")}')`, ['User.Read']);
		// mySecurityGroups = await response.json();
	}
	// console.log(
	// 	'=== src - routes - layout - protected - identities - page.server.ts - azure_token_groups ==='
	// );
	// console.log(locals.sessionData.currentUser?.azure_token_groups.join("','"));

	// console.log('=== src - routes - layout - protected - identities - +page.server.ts - mySecurityGroups ===');
	// console.log(mySecurityGroups);

	// console.log('=== src - routes - layout - protected - identities - +page.server.ts - myTeams ===');
	// console.log(myTeams);

	const ueberGroups: UeberGroup[] = [];
	if (locals.sessionData.currentUser && locals.sessionData.currentUser.ueber_groups) {
		for (const groupId of locals.sessionData.currentUser.ueber_groups) {
			const response = await backendAPI.get(sessionId, `/uebergroup/${groupId}`);
			if (response.status === 200) {
				const ueberGroup = await response.json();
				ueberGroups.push(ueberGroup);
			} else {
				console.error('Failed to fetch ueber group with ID:', groupId, 'Status:', response.status);
			}
		}
	}

	return {
		microsoftTeams: myTeams,
		ueberGroups
	};
};
