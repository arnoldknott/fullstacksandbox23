import { microsoftGraph } from "./msgraph";
import type { User } from '$lib/types';
import type { User as AzureUser } from '@microsoft/microsoft-graph-types';
import type { SvelteMap } from "svelte/reactivity";

// type linkedAzureAccount = SvelteMap<string, AzureUser>;

class MicrosoftAccountLinking {
    constructor() { }

    async getMicrosoftUser(sessionId: string, users: User[]) {
        const azureUsers: AzureUser[] = [];
        for (const user of users) {
            const responseAzureUsers = await microsoftGraph.get(
                sessionId,
                `/users/${user.azure_user_id}`
            );
            const azureUser: AzureUser = await responseAzureUsers.json();
            azureUsers.push(azureUser);
        }
        return azureUsers;
    }
}

export const microsoftAccountLinking = new MicrosoftAccountLinking();