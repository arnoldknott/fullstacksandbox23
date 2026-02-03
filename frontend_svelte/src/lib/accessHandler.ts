import type { AccessPolicy, AccessShareOption, Identity, MicrosoftTeamExtended } from '$lib/types';

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
	MICROSOFT_TEAM
}

export class AccessHandler {
	static getRights(identityId?: string, accessPolicies?: AccessPolicy[]): Action | undefined {
		const hasOwnerRights = accessPolicies?.some(
			(policy) => policy.identity_id === identityId && policy.action === Action.OWN
		);
		const hasWriteRights = accessPolicies?.some(
			(policy) => policy.identity_id === identityId && policy.action === Action.WRITE
		);
		const hasConnectRights = accessPolicies?.some(
			(policy) => policy.identity_id === identityId && policy.action === Action.CONNECT
		);
		const hasReadRights = accessPolicies?.some(
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

	static reduceMicrosoftTeamsToIdentities(microsoftTeams: MicrosoftTeamExtended[]): Identity[] {
		return microsoftTeams
			.filter((team: MicrosoftTeamExtended) => team.id !== undefined)
			.map((team: MicrosoftTeamExtended) => ({
				id: team.id as string,
				name: team.displayName || 'Unknown Team',
				type: IdentityType.MICROSOFT_TEAM
			}));
	}

	static createShareOptions(
		identities?: Identity[],
		accessPolicies?: AccessPolicy[]
	): AccessShareOption[] | undefined {
		return identities
			?.map((identity: Identity) => {
				return {
					identity_id: identity.id,
					identity_name: identity.name,
					identity_type: identity.type,
					action: AccessHandler.getRights(identity.id, accessPolicies),
					public: false
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
			default:
				return 'icon-[ic--round-question-mark]';
		}
	};
}
