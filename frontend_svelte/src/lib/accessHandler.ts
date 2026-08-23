import type { AccessPolicy, AccessShareOption, Identity } from '$lib/types';

export enum Action {
	OWN = 'own',
	WRITE = 'write',
	CONNECT = 'connect',
	READ = 'read'
}

// numerical here to allow sorting by type
export enum IdentityType {
	USER,
	UEBER_GROUP,
	GROUP,
	SUB_GROUP,
	SUB_SUB_GROUP,
	MICROSOFT_TEAM,
	PUBLIC
}

// Stable client-side id for the singleton public identity ("All users").
// It is never sent to the backend as an identity_id: public access is expressed
// through the `public` flag on an AccessPolicy instead.
export const PUBLIC_IDENTITY_ID = 'public';

export class AccessHandler {
	static getRights(identityId?: string, accessPolicies?: AccessPolicy[]): Action | undefined {
		// check for the highest level of access for the given identityId in the accessPolicies array
		let hasOwnerRights;
		let hasWriteRights;
		let hasConnectRights;
		let hasReadRights;
		// check for highest level of access for the public identity in the accessPolicies array
		if (identityId === PUBLIC_IDENTITY_ID) {
			hasOwnerRights = accessPolicies?.find(
				(policy) => policy.public === true && policy.action === Action.OWN
			);
			hasWriteRights = accessPolicies?.find(
				(policy) => policy.public === true && policy.action === Action.WRITE
			);
			hasConnectRights = accessPolicies?.find(
				(policy) => policy.public === true && policy.action === Action.CONNECT
			);
			hasReadRights = accessPolicies?.find(
				(policy) => policy.public === true && policy.action === Action.READ
			);
		}
		hasOwnerRights =
			hasOwnerRights ||
			accessPolicies?.some(
				(policy) => policy.identity_id === identityId && policy.action === Action.OWN
			);
		hasWriteRights =
			hasWriteRights ||
			accessPolicies?.some(
				(policy) => policy.identity_id === identityId && policy.action === Action.WRITE
			);
		hasConnectRights =
			hasConnectRights ||
			accessPolicies?.some(
				(policy) => policy.identity_id === identityId && policy.action === Action.CONNECT
			);
		hasReadRights =
			hasReadRights ||
			accessPolicies?.some(
				(policy) => policy.identity_id === identityId && policy.action === Action.READ
			);
		if (hasOwnerRights) {
			return Action.OWN;
		} else if (hasWriteRights) {
			return Action.WRITE;
		} else if (hasConnectRights) {
			return Action.CONNECT;
		} else if (hasReadRights) {
			return Action.READ;
		} else {
			return undefined;
		}
	}

	static createShareOptions(
		identities?: Identity[],
		accessPolicies?: AccessPolicy[]
	): AccessShareOption[] | undefined {
		return identities
			?.map((identity: Identity) => {
				const isPublic = identity.type === IdentityType.PUBLIC;
				return {
					// the public identity has no backend identity_id: it maps to the `public` flag
					// TBD: refactor to use PUBLIC_IDENTITY_ID
					identity_id: isPublic ? undefined : identity.id,
					identity_name: identity.name,
					identity_type: identity.type,
					action: AccessHandler.getRights(identity.id, accessPolicies),
					public: isPublic
				};
			})
			.sort((a: AccessShareOption, b: AccessShareOption) => {
				return a.identity_type - b.identity_type || a.identity_name.localeCompare(b.identity_name);
			});
	}

	// TBD: consider moving this to a designHandler or iconHandler or entityDesigner?
	static rightsIcon = (right?: Action) => {
		switch (right) {
			case Action.OWN:
				return `icon-[tabler--key-filled] bg-${this.rightsIconColor(right)}`;
			case Action.WRITE:
				return `icon-[material-symbols--edit-outline-rounded] bg-${this.rightsIconColor(right)}`;
			case Action.CONNECT:
				return `icon-[fa7-solid--link] bg-${this.rightsIconColor(right)}`;
			case Action.READ:
				return `icon-[tabler--eye] bg-${this.rightsIconColor(right)}`;
			default:
				return `icon-[tabler--ban] bg-${this.rightsIconColor(right)}`;
		}
	};

	static rightsIconColor = (right?: Action) => {
		switch (right) {
			case Action.OWN:
				return 'success';
			case Action.WRITE:
				return 'warning';
			case Action.CONNECT:
				return 'info';
			case Action.READ:
				return 'neutral';
			default:
				return 'error';
		}
	};

	static rightsIconEmoji = (right?: Action) => {
		switch (right) {
			case Action.OWN:
				return '🔑';
			case Action.WRITE:
				return '✏️';
			case Action.CONNECT:
				return '🔗';
			case Action.READ:
				return '👁️';
			default:
				return '🚫';
		}
	};

	static identityIcon = (identityType: IdentityType) => {
		switch (identityType) {
			case IdentityType.USER:
				return 'icon-[fa6-solid--user]';
			case IdentityType.UEBER_GROUP:
				return 'icon-[fa--institution]';
			case IdentityType.GROUP:
				return 'icon-[ph--users-four-fill]';
			case IdentityType.SUB_GROUP:
				return 'icon-[fa--users]';
			case IdentityType.SUB_SUB_GROUP:
				return 'icon-[fa6-solid--user-group]';
			case IdentityType.MICROSOFT_TEAM:
				return 'icon-[fluent--people-team-16-filled]';
			case IdentityType.PUBLIC:
				return 'icon-[gis--globe-earth-alt]';
			default:
				return 'icon-[ic--round-question-mark]';
		}
	};
}
