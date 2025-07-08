import AppConfig from '$lib/server/config';
import { BaseAPI, type RequestBody } from './base';
import { msalAuthProvider } from '$lib/server/oauth';
// import type { MicrosoftTeamBasic } from '$lib/types';
import type { Team } from '@microsoft/microsoft-graph-types';

const appConfig = await AppConfig.getInstance();

class MicrosoftGraph extends BaseAPI {
	appConfig: AppConfig;

	constructor() {
		super(msalAuthProvider, appConfig.ms_graph_base_uri);
		this.appConfig = appConfig;
	}

	async post(
		sessionId: string,
		path: string,
		body: RequestBody,
		scopes: string[] = ['User.Read'],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.post(sessionId, path, body, scopes, options, headers);
	}

	async get(
		sessionId: string,
		path: string,
		scopes: string[] = ['User.Read'],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.get(sessionId, path, scopes, options, headers);
	}

	// TBD: implement put and delete methods

	async getAttachedTeams(sessionId: string, azureGroups: string[]) {
		// const myTeams: MicrosoftTeamBasic[] = [];
		const myTeams: Team[] = [];
		await Promise.all(
			azureGroups.map(async (azureGroup) => {
				const response = await this.get(sessionId, `/teams/${azureGroup}`, ['Team.ReadBasic.All']);
				if (response.status === 200) {
					const microsoftTeam = await response.json();
					myTeams.push(microsoftTeam);
					// myTeams.push({
					// 	id: microsoftTeam.id,
					// 	displayName: microsoftTeam.displayName,
					// 	description: microsoftTeam.description
					// });
				}
			})
		);
		return myTeams;
	}

	// async getAttachedSecuriyGroups(sessionId: string, azureGroups: string[]) {
	// const mySecurityGroups: any[] = [];
	// await Promise.all(
	// 	azureGroups.map(async (azureGroup) => {
	// 		// const response = await this.get(sessionId, `/me/memberOf/microsoft.graph.group?$search="id:${azureGroup}"`, ['User.Read']);
	// 		const response = await this.get(sessionId, `/me/memberOf/`, ['User.Read']);
	// 		if (response.status === 200) {
	// 			const securityGroup = await response.json();
	// 			mySecurityGroups.push({ securityGroup });
	// 		};

	// 	})
	// )
	// return this.get(sessionId, `/me/memberOf/`, ['User.Read'])
	// return mySecurityGroups;
	// }
}

export const microsoftGraph = new MicrosoftGraph();
