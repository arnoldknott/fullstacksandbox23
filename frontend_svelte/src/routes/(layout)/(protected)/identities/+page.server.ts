import type { Team as MicrosoftTeam } from '@microsoft/microsoft-graph-types';

// import type { MicrosoftTeamBasic } from '$lib/types';
import { backendAPI } from '$lib/server/apis/backendApi';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import type { UeberGroupExtended } from '$lib/types';

import type { PageServerLoad } from './$types';
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
	let ueberGroups: UeberGroupExtended[] = [];
	let ueberGroupCursor = 0;
	if (locals.sessionData.currentUser) {
		const snapshot = await backendAPI.getSnapshot<UeberGroupExtended>(
			sessionId,
			'/uebergroup/snapshot?include=creation-date&sort=creation-date&direction=desc'
		);
		ueberGroups = snapshot.entities;
		ueberGroupCursor = snapshot.cursor;
	}

	// This is only updating when a session is getting refreshed - that might take weeks: not good!
	// let ueberGroups: UeberGroup[] = [];
	// if (locals.sessionData.currentUser && locals.sessionData.currentUser.ueber_groups) {
	// 	ueberGroups = locals.sessionData.currentUser.ueber_groups;
	// }

	return {
		microsoftTeams: myTeams,
		ueberGroups,
		ueberGroupCursor
	};
};
