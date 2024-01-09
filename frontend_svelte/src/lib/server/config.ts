import dotenv from 'dotenv';
dotenv.config();


import { ManagedIdentityCredential } from "@azure/identity";
import { SecretClient } from "@azure/keyvault-secrets";
import type { Configuration } from '$lib/types';


export const app_config = async () => {
	const configuration: Configuration = {
		backend_host: process.env.BACKEND_HOST,
		api_scope: '',
		app_reg_client_id: '',
		app_client_secret: '',
		azure_authority: process.env.AZURE_AUTHORITY,
		redis_host: process.env.REDIS_HOST,
		redis_port: process.env.REDIS_PORT,
		redis_session_db: process.env.REDIS_SESSION_DB,
		redis_password: ''
	}
	if (process.env.AZURE_KEYVAULT_HOST) {
		console.log("app_config - process.env.AZURE_KEYVAULT_HOST: ");
		console.log(process.env.AZURE_KEYVAULT_HOST);
		const credential = new ManagedIdentityCredential();
		const client = new SecretClient(process.env.AZURE_KEYVAULT_HOST, credential);
		const keyvaultHealth = await client.getSecret('keyvault-health');
		console.log("app_config - keyvaultHealth: ");
		console.log(keyvaultHealth);
		console.log("app_config - keyvaultHealth.value: ");
		console.log(keyvaultHealth.value);
		const appRegClientId = await client.getSecret('app-reg-client-id');
		const appClientSecret = await client.getSecret('app-client-secret');
		const apiScope = await client.getSecret('api-scope');
		const redisPassword = await client.getSecret('redis-password');
		configuration.keyvault_health = keyvaultHealth.value;
		configuration.app_reg_client_id = appRegClientId.value || '';
		configuration.app_client_secret = appClientSecret.value || '';
		configuration.api_scope = apiScope.value || '';
		configuration.redis_password = redisPassword.value || '';
	}
	else {
		console.log("app_config - process.env.AZURE_KEYVAULT_HOST not set");
		configuration.keyvault_health = process.env.KEYVAULT_HEALTH;
		configuration.app_reg_client_id = process.env.APP_REG_CLIENT_ID;
		configuration.app_client_secret = process.env.APP_CLIENT_SECRET;
		configuration.api_scope = process.env.API_SCOPE;
		configuration.redis_password = process.env.REDIS_PASSWORD;
	};
return configuration;
};
