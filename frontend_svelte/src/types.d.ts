export type User = {
	email: string;
	password?: string;
	name?: string;
	loggedIn?: boolean;
};// TBD: remove

export type Configuration = {
	azure_authority: string;
	backend_host: string;
	app_reg_client_id: string;
	api_scope: string;
	keyvault_health?: string;
};
