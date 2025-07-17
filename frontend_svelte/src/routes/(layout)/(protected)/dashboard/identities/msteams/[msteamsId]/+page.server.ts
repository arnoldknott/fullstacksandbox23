import type { PageServerLoad } from './$types';
import { microsoftGraph } from '$lib/server/apis/msgraph';
// import type { MicrosoftTeamBasic } from '$lib/types';
import type { Team as MicrosoftTeam } from '@microsoft/microsoft-graph-types';
// const getAllMicrosoftTeams = async (sessionId: string, azureGroups: string[]) => {

// }

export const load: PageServerLoad = async ({ locals, params }) => {
	console.log(
		'=== src - routes - layout - protected - identities - teams - [msteamsId]  - +page.server.ts - locals ==='
	);
	console.log(locals);
	console.log(
		'=== src - routes - layout - protected - identities - teams - [msteamsId]  - +page.server.ts - params ==='
	);
	console.log(params);
	const sessionId = locals.sessionData.sessionId;

	let thisTeam: MicrosoftTeam = {};
	const response = await microsoftGraph.get(sessionId, `/teams/${params.msteamsId}`, [
		'Team.ReadBasic.All'
	]);
	if (response.status === 200) {
		thisTeam = await response.json();
	} else {
		console.error('Error fetching Microsoft Team:', response.status);
	}

	console.log(
		'=== src - routes - layout - protected - identities - +page.server.ts - thisTeam ==='
	);
	// console.log(thisTeam);

	return {
		thisTeam: thisTeam
	};
};
