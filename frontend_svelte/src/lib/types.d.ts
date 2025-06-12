import type { AccountInfo } from '@azure/msal-node';
import type { User as MicrosoftProfile } from '@microsoft/microsoft-graph-types';
import type { Action } from '$lib/accessHandler';

// App specific:
export type BackendAPIConfiguration = {
	backendFqdn: string;
	restApiPath: string;
	websocketPath: string;
	socketIOPath: string | null;
};

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
	microsoftAccount?: AccountInfo;
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

// Access types:
export interface AccessPolicy {
	resource_id: string;
	identity_id: string;
	action: Action;
	new_action?: Action; // for updates
	public?: boolean;
	id?: number;
}

export interface AccessRight {
	resource_id: string;
	action: Action;
}

// Generic for resources - and partially relevant for identities:
// Create a generic type that extends a base type with additional properties
type ExtendEntity<T> = T &
	Partial<WithCreationDate & WithLastModifiedDate & WithAccessRights & WithAccessPolicies>;

// Define the additional properties as separate interfaces
interface WithCreationDate {
	creation_date: Date;
}

interface WithLastModifiedDate {
	last_modified_date: Date;
}

// The user's own access rights
// intended for checking this user's rights
// highest permission wins: "own", "write", "read"
interface WithAccessRights {
	user_right: Action; // Adjust the type as needed
}

// Access policies for the resource - that includes other users' access permissions
// intended for sharing operations
interface WithAccessPolicies {
	access_policies: AccessPolicy[];
}

// specific resources:
export interface DemoResource {
	id?: string;
	name: string;
	description?: string;
	language?: string;
	category?: string;
	category_id?: string;
	tags?: string[];
}

// add all specific resources that share the extension properties here:
export type DemoResourceExtended = ExtendEntity<DemoResource>;

// TBD: consider moving this, to where it is used locally
// in protected/backend-demo-resource: +page.svelte;
// needs to be defined client side!
export interface DemoResourceWithCreationDate extends DemoResource {
	creation_date: Date;
}

// Identity specific:

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

export interface MicrosoftTeamBasic {
	id: string;
	displayName: string;
	description: string;
}

export type MicrosoftTeamBasicExtended = ExtendEntity<MicrosoftTeamBasic>;

// add types for ueber-group, group, sub-group, and sub-sub-group
