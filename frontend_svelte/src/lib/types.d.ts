import type { AccountInfo } from '@azure/msal-node';
import type {
	User as MicrosoftProfile,
	Team as MicrosoftTeam
} from '@microsoft/microsoft-graph-types';
import type { Action, IdentityType } from '$lib/accessHandler';
import type { Variant } from '$lib/theming';
import type { SessionStatus } from '$lib/session';

// App specific:
export type BackendAPIConfiguration = {
	backendFqdn: string;
	restApiPath: string;
	websocketPath: string;
	socketIOPath: string | null;
};

// TBD: rename into ServerSession:
export type Session = {
	loggedIn: boolean;
	status?: SessionStatus;
	microsoftAccount?: AccountInfo;
	microsoftProfile?: MicrosoftProfile;
	userAgent?: string;
	currentUser?: Me;
	sessionId: string;
};

export type ClientSession = {
	loggedIn: boolean;
	sessionId: string;
	microsoftProfile: MicrosoftProfile;
};

// Sidebar:

export type SidebarContent = {
	id: string;
	name: string;
	pathname: string;
	icon: string;
	items: SidebarContentItem[];
};

type SidebarLinkContent = {
	id: string;
	name: string;
	pathname?: string;
	hash?: string;
	icon: string;
};

type SidebarContentItem = SidebarFolderContent | SidebarLinkContent;
export type SidebarFolderContent = {
	id: string;
	name: string;
	pathname?: string;
	hash?: string;
	icon: string;
	items: SidebarContentItem[];
};

// Access types:
export interface AccessPolicy {
	resource_id: string;
	identity_id: string; // can be optional for public resources
	action?: Action;
	new_action?: Action; // for updates
	public?: boolean;
	id?: number;
}

// identifies with whom and how a resource can be shared with:
export interface AccessShareOption {
	identity_id: string;
	identity_name: string;
	identity_type: IdentityType;
	action?: Action; // for existing AccessPolicy for this identity: it's an Action, otherwise undefined
	public?: boolean;
}

export interface AccessRight {
	resource_id: string;
	action: Action;
}

export interface Hierarchy {
	child_id: string;
	parent_id: string;
	inherit?: boolean;
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
	access_right: Action; // Adjust the type as needed
}

// Access policies for the resource - that includes other users' access permissions
// intended for sharing operations
interface WithAccessPolicies {
	access_policies: AccessPolicy[];
}

interface WithAccessShareOptions {
	access_share_options: AccessShareOption[];
}

// specific resources:
export interface DemoResource {
	id: string;
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

export type Identity = {
	id: string;
	name: string;
	type: IdentityType;
};

export type User = {
	id: string;
	azure_user_id: string;
	azure_tenant_id: string;
	is_active: boolean;
	azure_groups: AzureGroup[];
	ueber_groups?: UeberGroup[]; // TBD: fix
	groups?: Group[]; // TBD: fix
	sub_groups?: SubGroup[]; // TBD: fix
	sub_sub_groups?: SubSubGroup[]; // TBD: fix
};

type UserProfile = {
	id: string;
	theme_color?: string;
	theme_variant?: Variant; // from theming.ts
	contrast?: number;
	user_id: string; // TBD: remove
};

type UserAccount = {
	id: string;
	user_id: string;
	is_publicAIIuser: boolean;
};

// matches Me in models/identities/backend API
export type Me = User & {
	azure_token_roles?: string[];
	azure_token_groups?: string[];
	user_profile: UserProfile;
	user_account: UserAccount;
};

type AzureGroup = {
	id: string;
	azure_tenant_id: string;
	is_active: boolean;
	azure_users: User[];
};

export type UeberGroup = {
	id: string;
	name: string;
	description?: string;
	users?: User[];
	groups?: Group[];
};

export type Group = {
	id: string;
	name: string;
	description?: string;
	users?: User[];
	sub_groups?: SubGroup[];
};

export type SubGroup = {
	id: string;
	name: string;
	description?: string;
	users?: User[];
	sub_sub_groups?: SubSubGroup[];
};

export type SubSubGroup = {
	id: string;
	name: string;
	description?: string;
	users?: User[];
};

export type UserExtended = ExtendEntity<User>;
export type UeberGroupExtended = ExtendEntity<UeberGroup>;
export type GroupExtended = ExtendEntity<Group>;
export type SubGroupExtended = ExtendEntity<SubGroup>;
export type SubSubGroupExtended = ExtendEntity<SubSubGroup>;
export type MicrosoftTeamExtended = MicrosoftTeam & Partial<WithAccessRights & WithAccessPolicies>;

export type AnyEntityExtended =
	| DemoResourceExtended
	| UserExtended
	| UeberGroupExtended
	| GroupExtended
	| SubGroupExtended
	| SubSubGroupExtended;

export type AnyGroupIdentity = UeberGroup | Group | SubGroup | SubSubGroup;
