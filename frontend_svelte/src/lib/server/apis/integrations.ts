import type { User } from '$lib/types';

import { microsoftGraph } from './msgraph';
// import type { User as MicrosoftUser } from '@microsoft/microsoft-graph-types';
// import type { SvelteMap } from 'svelte/reactivity';

// type linkedMicrosoftAccount = SvelteMap<string, MicrosoftUser>;

export class MicrosoftAccountLinking {
	constructor() {}

	// TBD: rename into getMicrosoftUsers?
	// would make more sense to put this into msgraphAPI, as it returns microsoft data.
	static async getUsers(sessionId: string, users: User[]) {
		const microsoftUsers = users.filter((user) => user.azure_user_id);
		if (microsoftUsers.length === 0) return [];
		const filter = microsoftUsers.map((user) => `id eq '${user.azure_user_id}'`).join(' or ');
		const response = await microsoftGraph.get(sessionId, `/users?$filter=(${filter})`);
		const responseData = await response.json();
		return responseData.value;
	}
}
