import dotenv from 'dotenv';
dotenv.config();

import { ManagedIdentityCredential } from "@azure/identity";
import { SecretClient } from "@azure/keyvault-secrets";


export const app_config = async () => {
	if (process.env.AZURE_KEYVAULT_HOST) {
		const credential = new ManagedIdentityCredential();
		const client = new SecretClient(process.env.AZURE_KEYVAULT_HOST, credential);
		const keyvaultHealth = await client.getSecret('keyvault-health');
		const appRegClientId = await client.getSecret('app-reg-client-id');
		return { 
			status: keyvaultHealth,
			backend_host: process.env.BACKEND_HOST,
			app_reg_client_id : appRegClientId,
			authority: process.env.AUTHORITY,
		 }; // TBD: change into actually retrieving KEYVAULT_HEALTH from KEYVAULT_HOST
	}
	return {
		status: process.env.KEYVAULT_HEALTH,
		app_reg_client_id: process.env.APP_REG_CLIENT_ID,
		backend_host: process.env.BACKEND_HOST,
		authority: process.env.AUTHORITY,
	};
};
