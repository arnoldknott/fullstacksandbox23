import type { AccountInfo } from '@azure/msal-node';
import type { User as MicrosoftProfile } from '@microsoft/microsoft-graph-types';

export type BackendAPIConfiguration = {
	backendFqdn: string;
	restApiPath: string;
	websocketPath: string;
	socketIOPath: string | null;
};

// matches Me in models/identities/backend API
export type UserProfile = {
	id: string;
	azureGroups?: string[]; // TBD: fix
	ueberGroups?: string[]; // TBD: fix
	groups?: string[]; // TBD: fix
	subGroups?: string[]; // TBD: fix
	subSubGroups?: string[]; // TBD: fix
	azure_token_roles?: string[]; // TBD: fix
	azure_token_groups?: string[]; // TBD: fix
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
	userProfile?: UserProfile;
	sessionId: string;
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
	active?: boolean;
};

enum Action {
	Own = 'own',
	Write = 'write',
	Read = 'read',
}

export interface DemoResource {
	id?: string;
	name: string;
	description?: string;
	language?: string;
	category?: string;
	category_id?: string;
	tags?: string[];
}

// TBD: consider moving this, to where it is used locally
// in protected/backend-demo-resource: +page.svelte;
// needs to be defined client side!
export interface DemoResourceWithCreationDate extends DemoResource {
	creation_date: Date;
}


export interface AccessPolicy {
	resource_id: string;
	identity_id: string;
	action: Action
	public: boolean;
	id: number;
}