import type { SecretClient, SecretProperties } from '@azure/keyvault-secrets';
import { describe, expect, test, vi } from 'vitest';

import {
	decodeEncryptionKey,
	loadKeyVaultEncryptionKeyring,
	loadLocalEncryptionKeyring
} from './config';
import { Encryption, type EncryptionEnvelope, type EncryptionKey } from './encryption';
import { decryptSessionValue, encryptSessionValue } from './sessionEncryption';

const key = Uint8Array.from({ length: 32 }, (_, index) => index);
const previousKey = Uint8Array.from({ length: 32 }, (_, index) => 31 - index);
const ancientKey = Uint8Array.from({ length: 32 }, () => 66);
const keyBase64 = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8=';
const previousKeyBase64 = 'Hx4dHBsaGRgXFhUUExIREA8ODQwLCgkIBwYFBAMCAQA=';
const ancientKeyBase64 = 'QkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkI=';
const fixtureEnvelope: EncryptionEnvelope = {
	version: 1,
	'key-version': 'fixture-v1',
	nonce: 'AAECAwQFBgcICQoL',
	ciphertext:
		'PCC3eKaAsWjSNfjg1IdaV6Gl4leCHitRTAiO4HNLLJBgc82T2q9muk7fXYXn6k15jToP+DSi6r4drQh/cZuBm4JZ6w+gtFRDYSk=',
	tag: '8i6o1+OdlhyE1j8+1nQH3w=='
};

function encryption(
	options: {
		currentVersion?: string;
		currentKey?: Uint8Array;
		historical?: EncryptionKey[];
	} = {}
): Encryption {
	return new Encryption({
		keys: [
			{ version: options.currentVersion ?? 'current', key: options.currentKey ?? key },
			...(options.historical ?? [])
		]
	});
}

describe('application encryption', () => {
	test('decrypts the shared Python/TypeScript fixture', () => {
		expect(
			encryption({ currentVersion: 'fixture-v1' }).decrypt(
				'msal:fixture-user',
				'$',
				fixtureEnvelope
			)
		).toEqual({
			access_token: 'secret-token',
			account: { homeAccountId: 'fixture-user' }
		});
	});

	test('reads current and every historical key', () => {
		const previousEnvelope = encryption({
			currentVersion: 'previous',
			currentKey: previousKey
		}).encrypt('linkedin:subject', '$', { idToken: 'previous' });
		const ancientEnvelope = encryption({
			currentVersion: 'ancient',
			currentKey: ancientKey
		}).encrypt('linkedin:subject', '$', { idToken: 'ancient' });
		const reader = encryption({
			historical: [
				{ version: 'previous', key: previousKey },
				{ version: 'ancient', key: ancientKey }
			]
		});
		expect(reader.decrypt('linkedin:subject', '$', previousEnvelope)).toEqual({
			idToken: 'previous'
		});
		expect(reader.decrypt('linkedin:subject', '$', ancientEnvelope)).toEqual({
			idToken: 'ancient'
		});
	});

	test.each(['nonce', 'ciphertext', 'tag'] as const)('rejects a modified %s', (field) => {
		const encoded = fixtureEnvelope[field];
		const envelope = {
			...fixtureEnvelope,
			[field]: `${encoded[0] === 'A' ? 'B' : 'A'}${encoded.slice(1)}`
		};
		expect(() =>
			encryption({ currentVersion: 'fixture-v1' }).decrypt('msal:fixture-user', '$', envelope)
		).toThrow(/authentication failed|nonce/);
	});

	test('binds the storage location and purpose as associated data', () => {
		const reader = encryption({ currentVersion: 'fixture-v1' });
		expect(() => reader.decrypt('msal:another-user', '$', fixtureEnvelope)).toThrow(
			'Encryption authentication failed.'
		);
		expect(() => reader.decrypt('msal:fixture-user', '$.moved', fixtureEnvelope)).toThrow(
			'Encryption authentication failed.'
		);
	});

	test('never falls back for unknown, malformed, or unencrypted values', () => {
		const reader = encryption({ currentVersion: 'fixture-v1' });
		expect(() =>
			reader.decrypt('msal:fixture-user', '$', {
				...fixtureEnvelope,
				'key-version': 'unknown'
			})
		).toThrow('Unknown encryption key version.');
		const malformed: Partial<EncryptionEnvelope> = { ...fixtureEnvelope };
		delete malformed.tag;
		expect(() => reader.decrypt('msal:fixture-user', '$', malformed)).toThrow(
			'Malformed encryption envelope.'
		);
		expect(() => reader.decrypt('linkedin:subject', '$', { idToken: 'legacy' })).toThrow(
			'Unencrypted protected value is not permitted.'
		);
	});

	test('rejects empty keyrings and missing local keys', () => {
		expect(() => new Encryption({ keys: [] })).toThrow('At least one encryption key is required.');
		expect(() => loadLocalEncryptionKeyring({})).toThrow(
			'At least one local encryption key is required.'
		);
	});

	test('loads three ordered local keys and rejects malformed configuration', () => {
		const keyring = loadLocalEncryptionKeyring({
			ENCRYPTION_KEY_1: keyBase64,
			ENCRYPTION_KEY_VERSION_1: 'current',
			ENCRYPTION_KEY_2: previousKeyBase64,
			ENCRYPTION_KEY_VERSION_2: 'previous',
			ENCRYPTION_KEY_3: ancientKeyBase64,
			ENCRYPTION_KEY_VERSION_3: 'ancient'
		});
		expect(keyring.keys.map(({ version }) => version)).toEqual(['current', 'previous', 'ancient']);
		expect(() => decodeEncryptionKey('YQ==', 'test')).toThrow('exactly 32 bytes');
		expect(() =>
			loadLocalEncryptionKeyring({
				ENCRYPTION_KEY_1: keyBase64
			})
		).toThrow('requires both key and version');
		expect(() =>
			loadLocalEncryptionKeyring({
				ENCRYPTION_KEY_1: keyBase64,
				ENCRYPTION_KEY_VERSION_1: 'current',
				ENCRYPTION_KEY_3: ancientKeyBase64,
				ENCRYPTION_KEY_VERSION_3: 'ancient'
			})
		).toThrow('contiguous indices');
	});

	test('encrypts session data at its existing whole and leaf boundaries', () => {
		const crypt = encryption();
		const session = {
			sessionId: 'fixture',
			loggedIn: true,
			linkedinSubject: 'subject',
			microsoftAccount: { homeAccountId: 'account', username: 'person@example.invalid' },
			currentUser: { id: 'user-id', settings: { locale: 'en' }, roles: ['user'] }
		};
		const stored = encryptSessionValue(crypt, 'session:fixture', '$', session) as typeof session;
		expect(JSON.stringify(stored)).not.toMatch(/person@example.invalid|user-id/);
		expect(stored.sessionId).toBe('fixture');
		expect(stored.linkedinSubject).toBe('subject');
		expect(decryptSessionValue(crypt, 'session:fixture', '$', stored)).toEqual(session);
		expect(
			decryptSessionValue(crypt, 'session:fixture', '$.microsoftAccount', stored.microsoftAccount)
		).toEqual(session.microsoftAccount);
		const encryptedId = (stored.currentUser as unknown as { id: EncryptionEnvelope }).id;
		expect(decryptSessionValue(crypt, 'session:fixture', '$.currentUser.id', encryptedId)).toBe(
			'user-id'
		);
	});

	test('rejects deeper access beneath a whole encrypted subdocument', () => {
		const crypt = encryption();
		expect(() =>
			encryptSessionValue(crypt, 'session:fixture', '$.microsoftAccount.username', 'name')
		).toThrow('whole-value writes');
		expect(() =>
			decryptSessionValue(crypt, 'session:fixture', '$.microsoftAccount.username', 'value')
		).toThrow('whole-value reads');
	});
});

type SyntheticSecret = { value?: string; properties: SecretProperties };

function secret(version: string, value: string, createdOn: Date, enabled = true): SyntheticSecret {
	return {
		value,
		properties: {
			name: 'application-encryption-key',
			vaultUrl: 'https://vault.invalid',
			version,
			createdOn,
			enabled
		}
	};
}

function vaultClient(
	latestVersions: string[],
	versions: SecretProperties[],
	values: Record<string, SyntheticSecret | Error>
): SecretClient {
	const latest = [...latestVersions];
	return {
		getSecret: vi.fn(async (_name: string, options?: { version?: string }) => {
			const version = options?.version ?? latest.shift();
			if (!version) throw new Error('No synthetic latest version.');
			const value = values[version];
			if (value instanceof Error) throw value;
			return value;
		}),
		listPropertiesOfSecretVersions: vi.fn(() => ({
			async *[Symbol.asyncIterator]() {
				for (const version of versions) yield version;
			}
		}))
	} as unknown as SecretClient;
}

describe('Key Vault application-encryption discovery', () => {
	test('loads every version newest to oldest from unsorted metadata', async () => {
		const now = Date.now();
		const ancient = secret('ancient', ancientKeyBase64, new Date(now - 2_000));
		const previous = secret('previous', previousKeyBase64, new Date(now - 1_000));
		const current = secret('current', keyBase64, new Date(now));
		const client = vaultClient(
			['current', 'current'],
			[previous.properties, ancient.properties, current.properties],
			{ ancient, previous, current }
		);
		const keyring = await loadKeyVaultEncryptionKeyring(client);
		expect(keyring.keys.map(({ version }) => version)).toEqual(['current', 'previous', 'ancient']);
		expect(Array.from(keyring.keys[2].key)).toEqual(Array.from(ancientKey));
		expect(client.getSecret).toHaveBeenCalledTimes(4);
	});

	test('supports first generation and retries a startup rotation race', async () => {
		const previous = secret('previous', previousKeyBase64, new Date(Date.now() - 1_000));
		const current = secret('current', keyBase64, new Date());
		let client = vaultClient(['current', 'current'], [current.properties], { current });
		expect(
			(await loadKeyVaultEncryptionKeyring(client)).keys.map(({ version }) => version)
		).toEqual(['current']);
		client = vaultClient(
			['previous', 'current', 'current'],
			[previous.properties, current.properties],
			{ previous, current }
		);
		expect(
			(await loadKeyVaultEncryptionKeyring(client)).keys.map(({ version }) => version)
		).toEqual(['current', 'previous']);
		expect(client.listPropertiesOfSecretVersions).toHaveBeenCalledTimes(2);
	});

	test('rejects ambiguous, disabled, permission, and unavailable history', async () => {
		const createdOn = new Date();
		const current = secret('current', keyBase64, createdOn);
		const ambiguous = secret('ambiguous', previousKeyBase64, createdOn);
		let client = vaultClient(['current'], [current.properties, ambiguous.properties], {
			current,
			ambiguous
		});
		await expect(loadKeyVaultEncryptionKeyring(client)).rejects.toThrow('ambiguous');
		const disabled = secret('disabled', previousKeyBase64, new Date(0), false);
		client = vaultClient(['current'], [current.properties, disabled.properties], {
			current,
			disabled
		});
		await expect(loadKeyVaultEncryptionKeyring(client)).rejects.toThrow('disabled');
		const denied = {
			getSecret: vi.fn(async () => current),
			listPropertiesOfSecretVersions: vi.fn(() => {
				throw new Error('denied');
			})
		} as unknown as SecretClient;
		await expect(loadKeyVaultEncryptionKeyring(denied)).rejects.toThrow('denied');
		const unavailable = secret('unavailable', previousKeyBase64, new Date(0));
		client = vaultClient(['current'], [current.properties, unavailable.properties], {
			current,
			unavailable: new Error('unavailable')
		});
		await expect(loadKeyVaultEncryptionKeyring(client)).rejects.toThrow('unavailable');
	});
});
