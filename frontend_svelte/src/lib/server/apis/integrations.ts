import { microsoftGraph } from './msgraph';
import type { User } from '$lib/types';
import type { User as MicrosoftUser } from '@microsoft/microsoft-graph-types';
import type { SvelteMap } from 'svelte/reactivity';

type linkedMicrosoftAccount = SvelteMap<string, MicrosoftUser>;

export class MicrosoftAccountLinking {
	constructor() {}

	static async getUsers(sessionId: string, users: User[]) {
		const filter = users.map((user) => `id eq '${user.azure_user_id}'`).join(' or ');
		const response = await microsoftGraph.get(sessionId, `/users?$filter=(${filter})`);
		const responseData = await response.json();
		return responseData.value;
	}
}
