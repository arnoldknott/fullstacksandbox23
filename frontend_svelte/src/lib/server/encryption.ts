import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';

import type { SecretClient, SecretProperties } from '@azure/keyvault-secrets';

export const ENVELOPE_VERSION = 1;

export type EncryptionEnvelope = {
	version: number;
	'key-version': string;
	nonce: string;
	ciphertext: string;
	tag: string;
};

export type EncryptionKey = {
	version: string;
	key: Uint8Array;
};

export type EncryptionKeyring = {
	/** Keys ordered newest to oldest; index zero encrypts new data. */
	keys: EncryptionKey[];
};

const envelopeFields = ['version', 'key-version', 'nonce', 'ciphertext', 'tag'] as const;

function associatedData(location: string, purpose: string, keyVersion: string): Buffer {
	const part = (value: string) => `${Buffer.byteLength(value, 'utf8')}:${value}`;
	return Buffer.from(
		`application-encryption|${ENVELOPE_VERSION}|${part(keyVersion)}|${part(location)}|${part(purpose)}`,
		'utf8'
	);
}

export function isEncryptionEnvelope(value: unknown): value is EncryptionEnvelope {
	return (
		typeof value === 'object' &&
		value !== null &&
		Object.keys(value).length === envelopeFields.length &&
		envelopeFields.every((field) => Object.hasOwn(value, field))
	);
}

export function resemblesEncryptionEnvelope(value: unknown): boolean {
	return (
		typeof value === 'object' &&
		value !== null &&
		envelopeFields.some((field) => Object.hasOwn(value, field))
	);
}

export function decodeEncryptionKey(value: string, label: string): Uint8Array {
	if (!/^[A-Za-z0-9+/]+={0,2}$/.test(value) || value.length % 4 !== 0) {
		throw new Error(`${label} must be valid Base64.`);
	}
	const key = Buffer.from(value, 'base64');
	if (key.byteLength !== 32 || key.toString('base64') !== value) {
		throw new Error(`${label} must decode to exactly 32 bytes.`);
	}
	return key;
}

function decodeEnvelopeField(value: unknown, label: string): Buffer {
	if (
		typeof value !== 'string' ||
		!/^[A-Za-z0-9+/]+={0,2}$/.test(value) ||
		value.length % 4 !== 0
	) {
		throw new Error(`Malformed encryption ${label}.`);
	}
	const decoded = Buffer.from(value, 'base64');
	if (decoded.toString('base64') !== value) {
		throw new Error(`Malformed encryption ${label}.`);
	}
	return decoded;
}

export class Encryption {
	private readonly keysByVersion: Map<string, EncryptionKey>;

	constructor(private readonly keyring: EncryptionKeyring) {
		if (!keyring.keys[0]) throw new Error('At least one encryption key is required.');
		for (const entry of keyring.keys) {
			if (!entry.version || entry.key.byteLength !== 32) {
				throw new Error('Encryption keys require a version and 32 bytes.');
			}
		}
		this.keysByVersion = new Map(keyring.keys.map((entry) => [entry.version, entry]));
		if (this.keysByVersion.size !== keyring.keys.length) {
			throw new Error('Encryption key versions must be unique.');
		}
	}

	encrypt(location: string, purpose: string, value: unknown): unknown {
		const current = this.keyring.keys[0];
		const nonce = randomBytes(12);
		const cipher = createCipheriv('aes-256-gcm', current.key, nonce);
		cipher.setAAD(associatedData(location, purpose, current.version));
		const ciphertext = Buffer.concat([
			cipher.update(JSON.stringify(value), 'utf8'),
			cipher.final()
		]);
		return {
			version: ENVELOPE_VERSION,
			'key-version': current.version,
			nonce: nonce.toString('base64'),
			ciphertext: ciphertext.toString('base64'),
			tag: cipher.getAuthTag().toString('base64')
		} satisfies EncryptionEnvelope;
	}

	decrypt(location: string, purpose: string, value: unknown): unknown {
		if (!isEncryptionEnvelope(value)) {
			if (resemblesEncryptionEnvelope(value)) throw new Error('Malformed encryption envelope.');
			throw new Error('Unencrypted protected value is not permitted.');
		}
		if (value.version !== ENVELOPE_VERSION) {
			throw new Error(`Unsupported encryption envelope version: ${value.version}.`);
		}
		if (typeof value['key-version'] !== 'string') {
			throw new Error('Malformed encryption key version.');
		}
		const entry = this.keysByVersion.get(value['key-version']);
		if (!entry) throw new Error('Unknown encryption key version.');
		const nonce = decodeEnvelopeField(value.nonce, 'nonce');
		const ciphertext = decodeEnvelopeField(value.ciphertext, 'ciphertext');
		const tag = decodeEnvelopeField(value.tag, 'tag');
		if (nonce.byteLength !== 12 || tag.byteLength !== 16) {
			throw new Error('Malformed encryption nonce or tag.');
		}
		let plaintext: Buffer;
		try {
			const decipher = createDecipheriv('aes-256-gcm', entry.key, nonce);
			decipher.setAAD(associatedData(location, purpose, entry.version));
			decipher.setAuthTag(tag);
			plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
		} catch (cause) {
			throw new Error('Encryption authentication failed.', { cause });
		}
		return JSON.parse(plaintext.toString('utf8')) as unknown;
	}
}

function localKeys(environment: NodeJS.ProcessEnv): EncryptionKey[] {
	const keyIndices = Object.keys(environment)
		.map((name) => /^ENCRYPTION_KEY_(\d+)$/.exec(name)?.[1])
		.filter((index): index is string => index !== undefined)
		.map(Number);
	const versionIndices = Object.keys(environment)
		.map((name) => /^ENCRYPTION_KEY_VERSION_(\d+)$/.exec(name)?.[1])
		.filter((index): index is string => index !== undefined)
		.map(Number);
	const configured = [...new Set([...keyIndices, ...versionIndices])].sort((a, b) => a - b);
	if (configured.length === 0) return [];
	const expected = Array.from({ length: configured.at(-1)! }, (_, index) => index + 1);
	if (configured.some((value, index) => value !== expected[index])) {
		throw new Error('Local encryption keys must use contiguous indices from 1.');
	}
	return expected.map((index) => {
		const keyName = `ENCRYPTION_KEY_${index}`;
		const versionName = `ENCRYPTION_KEY_VERSION_${index}`;
		const value = environment[keyName];
		const version = environment[versionName];
		if (!value || !version) throw new Error(`${keyName} requires both key and version.`);
		return { version, key: decodeEncryptionKey(value, keyName) };
	});
}

export function loadLocalEncryptionKeyring(
	environment: NodeJS.ProcessEnv = process.env
): EncryptionKeyring {
	const keys = localKeys(environment);
	if (!keys[0]) throw new Error('At least one local encryption key is required.');
	return { keys };
}

function createdAt(properties: SecretProperties): number {
	const timestamp = properties.createdOn?.getTime();
	if (timestamp === undefined || !Number.isFinite(timestamp)) {
		throw new Error('Encryption secret version is missing its creation time.');
	}
	return timestamp;
}

export async function loadKeyVaultEncryptionKeyring(
	client: SecretClient
): Promise<EncryptionKeyring> {
	const secretName = 'application-encryption-key';
	for (let attempt = 0; attempt < 3; attempt++) {
		const firstLatest = await client.getSecret(secretName);
		if (!firstLatest.value || !firstLatest.properties.version) {
			throw new Error('Current encryption secret is incomplete.');
		}

		const versions: SecretProperties[] = [];
		for await (const properties of client.listPropertiesOfSecretVersions(secretName)) {
			versions.push(properties);
		}
		const ordered = [...versions].sort((left, right) => createdAt(right) - createdAt(left));
		if (ordered[0]?.version !== firstLatest.properties.version) {
			continue;
		}
		const createdTimes = ordered.map(createdAt);
		if (new Set(createdTimes).size !== createdTimes.length) {
			throw new Error('Encryption secret version order is ambiguous.');
		}
		for (const properties of ordered) {
			if (!properties.version) throw new Error('Encryption secret metadata is missing a version.');
			if (properties.enabled === false) {
				throw new Error(`Encryption secret version ${properties.version} is disabled.`);
			}
		}

		const keys: EncryptionKey[] = [
			{
				version: firstLatest.properties.version,
				key: decodeEncryptionKey(firstLatest.value, secretName)
			}
		];
		for (const properties of ordered.slice(1)) {
			const version = properties.version!;
			const secret = await client.getSecret(secretName, { version });
			if (!secret.value || secret.properties.version !== version) {
				throw new Error(`Encryption secret version ${version} is incomplete.`);
			}
			keys.push({
				version,
				key: decodeEncryptionKey(secret.value, `${secretName} ${version}`)
			});
		}

		const secondLatest = await client.getSecret(secretName);
		if (secondLatest.properties.version !== firstLatest.properties.version) continue;
		return { keys };
	}
	throw new Error('Encryption secret rotated during startup discovery.');
}
