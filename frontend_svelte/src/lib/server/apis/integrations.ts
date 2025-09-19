import { microsoftGraph } from './msgraph';
import type { User } from '$lib/types';
import type { User as MicrosoftUser } from '@microsoft/microsoft-graph-types';
import type { SvelteMap } from 'svelte/reactivity';

type linkedMicrosoftAccount = SvelteMap<string, MicrosoftUser>;

export class MicrosoftAccountLinking {
	constructor() {}

	static async getUser(sessionId: string, users: User[]) {
		const microsoftUsers: MicrosoftUser[] = [];
		for (const user of users) {
			const responseMicrosoftUsers = await microsoftGraph.get(
				sessionId,
				`/users/${user.azure_user_id}`
			);
			const microsoftUser: MicrosoftUser = await responseMicrosoftUsers.json();
			microsoftUsers.push(microsoftUser);
		}
		return microsoftUsers;
	}
}
