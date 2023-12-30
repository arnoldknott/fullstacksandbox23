import dotenv, { config } from 'dotenv';
dotenv.config();

import { ManagedIdentityCredential } from "@azure/identity";
import { SecretClient } from "@azure/keyvault-secrets";
import type { Configuration } from 'src/types';


export const app_config = async () => {
	let configuration: Configuration = {
		backend_host: process.env.BACKEND_HOST,
		azure_authority: process.env.AUTHORITY,
	}
	if (process.env.AZURE_KEYVAULT_HOST) {
		const credential = new ManagedIdentityCredential();
		const client = new SecretClient(process.env.AZURE_KEYVAULT_HOST, credential);
		const keyvaultHealth = await client.getSecret('keyvault-health');
		const appRegClientId = await client.getSecret('app-reg-client-id');

		configuration.keyvault_health = keyvaultHealth.value;
		configuration.app_reg_client_id = appRegClientId.value;
	}
	else {
		configuration.keyvault_health = process.env.KEYVAULT_HEALTH;
		configuration.app_reg_client_id = process.env.APP_REG_CLIENT_ID;

	};
return configuration;
};
