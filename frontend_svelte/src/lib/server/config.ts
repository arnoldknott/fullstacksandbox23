import dotenv from 'dotenv';
dotenv.config();

import { ManagedIdentityCredential } from "@azure/identity";
import { SecretClient } from "@azure/keyvault-secrets";
import type { Configuration } from 'src/types';


export const app_config = async () => {
	const configuration: Configuration = {
		backend_host: process.env.BACKEND_HOST,
		api_scope: '',
		app_reg_client_id: '',
		azure_authority: process.env.AZURE_AUTHORITY,
	}
	if (process.env.AZURE_KEYVAULT_HOST) {
		const credential = new ManagedIdentityCredential();
		const client = new SecretClient(process.env.AZURE_KEYVAULT_HOST, credential);
		const keyvaultHealth = await client.getSecret('keyvault-health');
		const appRegClientId = await client.getSecret('app-reg-client-id');
		const apiScope = await client.getSecret('api-scope');

		configuration.keyvault_health = keyvaultHealth.value;
		configuration.app_reg_client_id = appRegClientId.value || '';
		configuration.api_scope = apiScope.value || '';
	}
	else {
		configuration.keyvault_health = process.env.KEYVAULT_HEALTH;
		configuration.app_reg_client_id = process.env.APP_REG_CLIENT_ID;
		configuration.api_scope = process.env.API_SCOPE;
	};
	console.log(configuration);
return configuration;
};
