import type { AccountInfo } from '@azure/msal-node';

export type BackendAPIConfiguration = {
	backendFqdn: string;
	restApiPath: string;
	websocketPath: string;
	socketIOPath: string | null;
};

export type User = {
	email: string;
	name?: string;
	loggedIn?: boolean;
}; // TBD: remove

// export type Configuration = {
// 	az_authority: string;
// 	backend_host: string;
// 	app_reg_client_id: string;
// 	app_client_secret: string;
// 	api_scope: string;
// 	backend_origin: string,
// 	keyvault_health?: string;
// 	ms_graph_base_uri: string
// 	redis_host: string;
// 	redis_port: string;
// 	redis_session_db: string;
// 	redis_password: string;
// };

export type Session = {
	loggedIn: boolean;
	microsoftAccount?: AccountInfo;// TBD: change to MicrosoftAccount, containing Account, IdToken, AccessToken, RefreshToken, AppMetadata
	userAgent?: string;
};

export type SocketioConnection = {
	event: string;
	namespace?: string;
	room?: string;
	connected?: boolean;
};

type Tab = {
	header: string;
	content: string;
	connection: SocketioConnection;
	active?: boolean;
};
