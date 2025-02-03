import type { AccessPolicy } from '$lib/types';

export enum Action {
	Own = 'own',
	Write = 'write',
	Read = 'read'
}

export class AccessHandler {
	static getRights(identityId: string, accessPolicies?: AccessPolicy[]) {
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
			return Action.Own;
		} else if (hasWriteRights) {
			return Action.Write;
		} else if (hasReadRights) {
			return Action.Read;
		} else {
			return null;
		}
	}
}
