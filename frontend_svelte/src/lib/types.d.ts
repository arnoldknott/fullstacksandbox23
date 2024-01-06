export type User = {
	email: string;
	name?: string;
	loggedIn?: boolean;
};// TBD: remove

export type Configuration = {
	azure_authority: string;
	backend_host: string;
	app_reg_client_id: string;
	app_client_secret: string;
	api_scope: string;
	keyvault_health?: string;
	redis_host: string;
	redis_port: string;
	redis_session_db: string;
	redis_password: string;
};
