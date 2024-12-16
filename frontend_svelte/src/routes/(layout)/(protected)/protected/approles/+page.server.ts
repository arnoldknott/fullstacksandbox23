import type { Actions } from './$types';
// import { ClientSecretCredential, DeviceCodeCredential} from '@azure/identity';
// import AppConfig from '$lib/server/config';
// import { AZURE_TENANT_ID, APP_REG_CLIENT_ID, APP_CLIENT_SECRET } from '$env/static/private';
// TBD: rename the BACKEND_SERVICE_PRINCIPLE_ID into whatever it's called elsewhere!
// TBD: change dynamic into static!:
// import { BACKEND_SERVICE_PRINCIPLE_ID, BACKEND_PUBLIC_AI_ROLE_ID } from '$env/static/private';
// import { Client } from '@microsoft/microsoft-graph-client';
// import { TokenCredentialAuthenticationProvider } from '@microsoft/microsoft-graph-client/authProviders/azureTokenCredentials';
// import '@microsoft/microsoft-graph-client//'
// import { SecretClient } from '@azure/keyvault-secrets';
// const appConfig = await AppConfig.getInstance();

export const actions = {
	toggleAIuser: async ({ request }) => {
		// const azureUserId = locals.sessionData.microsoftAccount?.localAccountId;
		// if (!azureUserId) {
		//     return {
		//         status: 401,
		//         body: { message: 'No user id!' }
		//     };
		// }
		const data = await request.formData();
		const { publicAIstatus } = Object.fromEntries(data);

		// const credential = new DeviceCodeCredential({
		//     tenantId: AZURE_TENANT_ID,
		//     clientId: APP_REG_CLIENT_ID,
		//     // clientId: appConfig.api_scope,
		//     userPromptCallback: (info) => console.log(info.message)
		// })

		// console.log('=== credential configured ===');

		// const credential = new ClientSecretCredential(
		//     AZURE_TENANT_ID,
		//     APP_REG_CLIENT_ID,
		//     APP_CLIENT_SECRET,
		// );
		// const authProvider = new TokenCredentialAuthenticationProvider(credential,
		//     {
		//         scopes: [
		//             // 'https://graph.microsoft.com/.default',
		//             'AppRoleAssignment.ReadWrite.All',// requires admin permissions beforehand for app registration
		//             'Application.Read.All'// requires admin permissions beforehand for app registration
		//         ]
		//     }
		//     // { scopes: [`api://${appConfig.api_scope}/.default`] }
		//     // { scopes: ['AppRoleAssignment.ReadWrite.All', 'Application.Read.All'] }
		// );

		// console.log('=== authProvider conducted and ready ===');

		// const graphClient = Client.initWithMiddleware({ authProvider: authProvider });

		if (publicAIstatus === 'on') {
			console.log('Enable AI role for user in backendAPI');
			// use ManagedIdentityCredential when deployed to Azure!
			// and maybe stick to old way of getting environmental variables due to different imports:
			// import dotenv from 'dotenv';
			// dotenv.config();
			// const credential = ManagedIdentityCredential(AZ_CLIENT_ID)
			// const appRoleAssignment = {
			//     principalId: azureUserId,// user id
			//     resourceId: BACKEND_SERVICE_PRINCIPLE_ID,// backendAPI SP id - the one, that has defined the appRole
			//     appRoleId: BACKEND_PUBLIC_AI_ROLE_ID// appRole id - of the app role that should be assigned
			// };

			// await graphClient.api(`/servicePrincipals/${BACKEND_SERVICE_PRINCIPLE_ID}/appRoleAssignedTo`)// backendAPI SP id
			//     .post(appRoleAssignment);
		} else {
			console.log('Disable AI role for user in backendAPI');
			//         const appRoleAssignedTo = await graphClient.api(`/servicePrincipals/${BACKEND_SERVICE_PRINCIPLE_ID}/appRoleAssignedTo`)
			// .get();
			// now, find the appRoleAssignment id for the user with the specific role id, and delete it:

			// await graphClient.api('/servicePrincipals/{resource-SP-id}/appRoleAssignedTo/{appRoleAssignment-id}').delete();
		}
	}
} satisfies Actions;
