import type { AccessPolicy } from '$lib/types';

export enum Action {
	OWN = 'own',
	WRITE = 'write',
	READ = 'read',
	UNSHARE = 'unshare'
}

export enum IdentityType {
	USER = 'user',
	UEBER_GROUP = 'ueber_group',
	GROUP = 'group',
	SUB_GROUP = 'sub_group',
	SUB_SUB_GROUP = 'sub_sub_group',
	MICROSOFT_TEAM = 'microsoft_team'
}

export class AccessHandler {
	static getRights(identityId: string, accessPolicies?: AccessPolicy[]): Action | undefined {
		const hasOwnerRights = accessPolicies?.some(
			(policy) => policy.identity_id === identityId && policy.action === 'own'
		);
		const hasWriteRights = accessPolicies?.some(
			(policy) => policy.identity_id === identityId && policy.action === 'write'
		);
		const hasReadRights = accessPolicies?.some(
			(policy) => policy.identity_id === identityId && policy.action === 'read'
		);
		if (hasOwnerRights) {
			return Action.OWN;
		} else if (hasWriteRights) {
			return Action.WRITE;
		} else if (hasReadRights) {
			return Action.READ;
		} else {
			return undefined;
		}
	}

	// TBD: consider moving this to a designHandler or iconHandler or entityDesigner?
	static rightsIcon = (right?: Action) => {
		switch (right) {
			case Action.OWN:
				return 'icon-[tabler--key-filled] bg-success';
			case Action.WRITE:
				return 'icon-[material-symbols--edit-outline-rounded] bg-warning';
			case Action.READ:
				return 'icon-[tabler--eye] bg-neutral';
			default:
				return 'icon-[tabler--ban] bg-error';
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
	}
}
