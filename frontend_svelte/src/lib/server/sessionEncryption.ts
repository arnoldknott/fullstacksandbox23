import { Encryption, isEncryptionEnvelope, resemblesEncryptionEnvelope } from './encryption';

const wholeProtectedRoots = new Set([
	'microsoftAccount',
	'microsoftAuthorization',
	'linkedinAuthorization',
	'accountMerge'
]);
const leafProtectedRoots = new Set(['currentUser']);
const protectedScalarRoots = new Set(['userAgent']);

function childPath(path: string, key: string | number): string {
	return typeof key === 'number' ? `${path}[${key}]` : `${path}.${key}`;
}

function encryptLeaves(
	encryption: Encryption,
	redisKey: string,
	path: string,
	value: unknown
): unknown {
	if (value === null || typeof value !== 'object') return encryption.encrypt(redisKey, path, value);
	if (Array.isArray(value)) {
		return value.map((item, index) =>
			encryptLeaves(encryption, redisKey, childPath(path, index), item)
		);
	}
	return Object.fromEntries(
		Object.entries(value).map(([key, item]) => [
			key,
			encryptLeaves(encryption, redisKey, childPath(path, key), item)
		])
	);
}

function decryptLeaves(
	encryption: Encryption,
	redisKey: string,
	path: string,
	value: unknown
): unknown {
	if (isEncryptionEnvelope(value) || resemblesEncryptionEnvelope(value)) {
		return encryption.decrypt(redisKey, path, value);
	}
	if (value === null || typeof value !== 'object') {
		return encryption.decrypt(redisKey, path, value);
	}
	if (Array.isArray(value)) {
		return value.map((item, index) =>
			decryptLeaves(encryption, redisKey, childPath(path, index), item)
		);
	}
	return Object.fromEntries(
		Object.entries(value).map(([key, item]) => [
			key,
			decryptLeaves(encryption, redisKey, childPath(path, key), item)
		])
	);
}

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
				if (wholeProtectedRoots.has(key) || protectedScalarRoots.has(key)) {
					return [key, encryption.encrypt(redisKey, itemPath, item)];
				}
				if (leafProtectedRoots.has(key)) {
					return [key, encryptLeaves(encryption, redisKey, itemPath, item)];
				}
				return [key, item];
			})
		);
	}
	const root = rootName(path);
	if (root && (wholeProtectedRoots.has(root) || protectedScalarRoots.has(root))) {
		if (path !== `$.${root}`) {
			throw new Error(`Protected session subdocument ${root} only supports whole-value writes.`);
		}
		return encryption.encrypt(redisKey, path, value);
	}
	if (root && leafProtectedRoots.has(root)) {
		return path === `$.${root}`
			? encryptLeaves(encryption, redisKey, path, value)
			: encryption.encrypt(redisKey, path, value);
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
				if (wholeProtectedRoots.has(key) || protectedScalarRoots.has(key)) {
					return [key, encryption.decrypt(redisKey, itemPath, item)];
				}
				if (leafProtectedRoots.has(key)) {
					return [key, decryptLeaves(encryption, redisKey, itemPath, item)];
				}
				return [key, item];
			})
		);
	}
	const root = rootName(path);
	if (root && (wholeProtectedRoots.has(root) || protectedScalarRoots.has(root))) {
		if (path !== `$.${root}`) {
			throw new Error(`Protected session subdocument ${root} only supports whole-value reads.`);
		}
		return encryption.decrypt(redisKey, path, value);
	}
	if (root && leafProtectedRoots.has(root)) {
		return path === `$.${root}`
			? decryptLeaves(encryption, redisKey, path, value)
			: encryption.decrypt(redisKey, path, value);
	}
	return value;
}
