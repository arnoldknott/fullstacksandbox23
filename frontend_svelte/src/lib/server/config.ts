import dotenv from 'dotenv';
dotenv.config();


import { ManagedIdentityCredential } from "@azure/identity";
import { SecretClient } from "@azure/keyvault-secrets";
import type { Configuration } from '$lib/types';


// TBD: turn into a class:
// export default class AppConfig{
// 	constructor(){
// 		const config = app_config()
// 		Object.assign(this, config);
// 	}
// }



export const app_config = async () => {
	const configuration: Configuration = {
		api_scope: '',
		app_reg_client_id: '',
		app_client_secret: '',
		az_authority: '',
		backend_host: process.env.BACKEND_HOST,
		backend_origin: `http://${process.env.BACKEND_HOST}:80`,
		ms_graph_base_uri: 'https://graph.microsoft.com/v1.0',
		redis_host: process.env.REDIS_HOST,
		redis_port: process.env.REDIS_PORT,
		redis_session_db: process.env.REDIS_SESSION_DB,
		redis_password: ''
	}
	// It seems that containerapps don't allow env-variables starting with AZURE_
	// Apparently that's a reserved namespace. So here AZ_ is used instead.
	if (process.env.AZ_KEYVAULT_HOST) {
		console.log("app_config - process.env.AZ_KEYVAULT_HOST: ");
		console.log(process.env.AZ_KEYVAULT_HOST);
		const credential = new ManagedIdentityCredential();
		const client = new SecretClient(process.env.AZ_KEYVAULT_HOST, credential);
		const keyvaultHealth = await client.getSecret('keyvault-health');
		console.log("app_config - keyvaultHealth: ");
		console.log(keyvaultHealth);
		console.log("app_config - keyvaultHealth.value: ");
		console.log(keyvaultHealth.value);
		const appRegClientId = await client.getSecret('app-reg-client-id');
		const appClientSecret = await client.getSecret('app-client-secret');
		const apiScope = await client.getSecret('api-scope');
		const az_tenant_id = await client.getSecret('azure_tenant_id');
		const redisPassword = await client.getSecret('redis-password');
		configuration.keyvault_health = keyvaultHealth.value;
		configuration.app_reg_client_id = appRegClientId.value || '';
		configuration.app_client_secret = appClientSecret.value || '';
		configuration.api_scope = apiScope.value || '';
		configuration.az_authority = `https://login.microsoftonline.com/${az_tenant_id.value}`,
		configuration.redis_password = redisPassword.value || '';
	}
	else {
		console.log("app_config - process.env.AZ_KEYVAULT_HOST not set");
		configuration.keyvault_health = process.env.KEYVAULT_HEALTH;
		configuration.app_reg_client_id = process.env.APP_REG_CLIENT_ID;
		configuration.app_client_secret = process.env.APP_CLIENT_SECRET;
		configuration.api_scope = process.env.API_SCOPE;
		configuration.redis_password = process.env.REDIS_PASSWORD;
	};
return configuration;
};

