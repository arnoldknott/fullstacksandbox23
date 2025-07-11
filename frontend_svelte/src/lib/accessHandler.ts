import type { AccessPolicy } from '$lib/types';

export enum Action {
	OWN = 'own',
	WRITE = 'write',
	READ = 'read',
	UNSHARE = 'unshare'
}

export class AccessHandler {
	static getRights(identityId: string, accessPolicies?: AccessPolicy[]): Action | null {
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
			return null;
		}
	}
}
