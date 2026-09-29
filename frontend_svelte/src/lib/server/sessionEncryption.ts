import { Encryption } from './encryption';

const wholeProtectedRoots = new Set([
	'microsoftAccount',
	'microsoftBackendAccessToken',
	'microsoftAuthorization',
	'linkedinAuthorization',
	'accountMerge'
]);
function rootName(path: string): string | undefined {
	return /^\$\.([^.[\]]+)/.exec(path)?.[1];
}

export function encryptSessionValue(
	encryption: Encryption,
	redisKey: string,
	path: string,
	value: unknown
): unknown {
	if (path === '$') {
		if (!value || typeof value !== 'object' || Array.isArray(value)) return value;
		return Object.fromEntries(
			Object.entries(value).map(([key, item]) => {
				const itemPath = `$.${key}`;
				if (wholeProtectedRoots.has(key)) {
					return [key, encryption.encrypt(redisKey, itemPath, item)];
				}
				return [key, item];
			})
		);
	}
	const root = rootName(path);
	if (root && wholeProtectedRoots.has(root)) {
		if (path !== `$.${root}`) {
			throw new Error(`Protected session subdocument ${root} only supports whole-value writes.`);
		}
		return encryption.encrypt(redisKey, path, value);
	}
	return value;
}

export function decryptSessionValue(
	encryption: Encryption,
	redisKey: string,
	path: string,
	value: unknown
): unknown {
	if (path === '$') {
		if (!value || typeof value !== 'object' || Array.isArray(value)) return value;
		return Object.fromEntries(
			Object.entries(value).map(([key, item]) => {
				const itemPath = `$.${key}`;
				if (wholeProtectedRoots.has(key)) {
					return [key, encryption.decrypt(redisKey, itemPath, item)];
				}
				return [key, item];
			})
		);
	}
	const root = rootName(path);
	if (root && wholeProtectedRoots.has(root)) {
		if (path !== `$.${root}`) {
			throw new Error(`Protected session subdocument ${root} only supports whole-value reads.`);
		}
		return encryption.decrypt(redisKey, path, value);
	}
	return value;
}
