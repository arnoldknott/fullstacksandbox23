import dotenv from 'dotenv';
dotenv.config();

export const app_config = async () => {
	if (process.env.AZURE_KEYVAULT_HOST) {
		return { AZURE_EYVAULT_HOST: process.env.AZURE_KEYVAULT_HOST }; // TBD: change into actually retrieving KEYVAULT_HEALTH from KEYVAULT_HOST
	}
	return { KEYVAULT_HEALTH: process.env.KEYVAULT_HEALTH };
};
