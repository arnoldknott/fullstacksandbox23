import type { AccountInfo } from '@azure/msal-node';
import type { User as MicrosoftProfile } from '@microsoft/microsoft-graph-types';

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

// TBD: rename into ServerSession:
export type Session = {
	loggedIn: boolean;
	status?: string;
	microsoftAccount?: AccountInfo; // TBD: change to MicrosoftAccount, containing Account, IdToken, AccessToken, RefreshToken, AppMetadata
	microsoftProfile?: MicrosoftProfile;
	userAgent?: string;
	sessionId?: string;
};

export type ClientSession = {
	loggedIn: boolean;
	sessionId: string;
	microsoftProfile: MicrosoftProfile;
};

export type SocketioConnection = {
	event: string;
	namespace?: string;
	room?: string;
	connected?: boolean;
	cookie_session_id?: string;
};

type Tab = {
	header: string;
	content: string;
	connection: SocketioConnection;
	active?: boolean;
};
