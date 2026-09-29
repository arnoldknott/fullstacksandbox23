import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';

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
