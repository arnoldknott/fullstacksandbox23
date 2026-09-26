import dotenv from 'dotenv';
dotenv.config();
// TBD: refactor to use sveltes built in env variables

import { ManagedIdentityCredential } from '@azure/identity';
import { SecretClient, type SecretProperties } from '@azure/keyvault-secrets';

import { building } from '$app/environment';

import { Encryption, type EncryptionKey, type EncryptionKeyring } from './encryption';
// import type { Configuration } from '$lib/types';

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

function localEncryptionKeys(environment: NodeJS.ProcessEnv): EncryptionKey[] {
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
	const keys = localEncryptionKeys(environment);
	if (!keys[0]) throw new Error('At least one local encryption key is required.');
	return { keys };
}

function encryptionKeyCreatedAt(properties: SecretProperties): number {
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
		const ordered = [...versions].sort(
			(left, right) => encryptionKeyCreatedAt(right) - encryptionKeyCreatedAt(left)
		);
		if (ordered[0]?.version !== firstLatest.properties.version) continue;
		const createdTimes = ordered.map(encryptionKeyCreatedAt);
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

export default class AppConfig {
	private static instance: AppConfig;
	public api_scope: string;
	public api_scope_default: string;
	public frontend_svelte_client_id: string;
	public frontend_svelte_client_secret: string;
	public az_authority: string;
	public az_logout_uri: string;
	public backend_host: string;
	public backend_origin: string;
	public backend_fqdn: string;
	public keyvault_health?: string;
	public ms_graph_base_uri: string;
	public linkedin_client_id: string;
	public linkedin_client_secret: string;
	public linkedin_issuer: string;
	public linkedin_api_base_uri: string;
	public redis_host: string;
	public redis_port: string;
	public redis_session_db: string;
	public redis_session_password: string;
	public authentication_timeout: number;
	// public authentication_cookie_options: object;
	public session_timeout: number;
	public session_cookie_options: object;
	public encryption?: EncryptionKeyring;
	private encryptionInstance?: Encryption;

	private constructor() {
		this.api_scope = '';
		this.api_scope_default = '';
		this.frontend_svelte_client_id = '';
		this.frontend_svelte_client_secret = '';
		this.az_authority = '';
		this.az_logout_uri = '';
		this.backend_host = ''; // process.env.BACKEND_HOST;
		this.backend_origin = ''; //`http://${process.env.BACKEND_HOST}:80`;
		this.backend_fqdn = '';
		this.keyvault_health = '';
		this.ms_graph_base_uri = 'https://graph.microsoft.com/v1.0';
		this.linkedin_client_id = '';
		this.linkedin_client_secret = '';
		this.linkedin_issuer = 'https://www.linkedin.com/oauth';
		this.linkedin_api_base_uri = 'https://api.linkedin.com/v2';
		this.redis_host = process.env.REDIS_HOST || '';
		this.redis_port = process.env.REDIS_PORT || '';
		this.redis_session_db = process.env.REDIS_SESSION_DB || '';
		this.redis_session_password = '';
		this.authentication_timeout = 60 * 10; // 10 minutes to authenticate
		// this.authentication_cookie_options = {};
		this.session_timeout = 60 * 120; // 2 hours
		this.session_cookie_options = {};
	}

	public static async getInstance(): Promise<AppConfig> {
		if (!AppConfig.instance) {
			AppConfig.instance = new AppConfig();
			await AppConfig.instance.updateValues();
		}
		return AppConfig.instance;
	}

	public getEncryption(): Encryption {
		if (!this.encryption) throw new Error('Encryption keyring is not configured.');
		return (this.encryptionInstance ??= new Encryption(this.encryption));
	}

	private async connectKeyvault(tries: number = 0): Promise<SecretClient> {
		try {
			// requires AZ_CLIENT_ID for keyvault access due to "working with AKS pod-identity" - see here:
			// https://learn.microsoft.com/en-us/javascript/api/@azure/identity/managedidentitycredential?view=azure-node-latest
			// console.log("📜 app_config - process.env.AZ_CLIENT_ID:");
			// console.log(process.env.AZ_CLIENT_ID);
			if (!process.env.AZ_CLIENT_ID || !process.env.AZ_KEYVAULT_HOST) {
				console.error(
					'🥞 app_config - server - connectKeyvault - keyvault connection data missing'
				);
				throw new Error(
					'🥞 app_config - server - connectKeyvault - keyvault connection data missing'
				);
			}
			const credential = new ManagedIdentityCredential(process.env.AZ_CLIENT_ID);
			const client = new SecretClient(process.env.AZ_KEYVAULT_HOST, credential);
			// throw new Error("⚡️ TEST ERROR ⚡️")// TBD for testing only!
			return client;
		} catch (err) {
			tries++;
			if (tries > 10) {
				console.error(
					`🥞 app_config - server - connectKeyvault - createClient failed after ${tries} tries`
				);
				throw err;
				// throw new Error("🥞 Connecting to Keyvault finally failed");
			}
			console.error('🥞 app_config - server - connectKeyvault - createClient failed');
			console.log(`Retry attempt ${tries} to connect to keyvault in 1 second`);
			await new Promise((resolve) => setTimeout(resolve, 5000));
			return this.connectKeyvault(tries);
		}
	}

	// TBD: make a button in the admin section, that calls this function to update the configuration values
	public async updateValues() {
		// SvelteKit imports server modules while analysing the build output. Runtime
		// configuration is loaded only after the built image starts in its target environment.
		if (building) return;

		// It seems that containerapps don't allow env-variables starting with AZURE_
		// Apparently that's a reserved namespace. So here AZ_ is used instead.
		if (process.env.AZ_KEYVAULT_HOST) {
			try {
				// console.log("📜 app_config - process.env.AZ_KEYVAULT_HOST:");
				// console.log(process.env.AZ_KEYVAULT_HOST);
				const client = await this.connectKeyvault();
				// console.log("📜 app_config - client:");
				// console.log(client);
				const keyvaultHealth = await client.getSecret('keyvault-health');
				const backend_host = await client.getSecret('backend-host');
				const backend_fqdn = await client.getSecret('backend-fqdn');
				// const backend_origin = await client?.getSecret('backend-origin');
				// const backend_host = this.backend_origin.split('://')[1].split(':')[0]; // replace("https://", "").split(":")[0]
				// console.log("📜 app_config - keyvaultHealth: ");
				// console.log(keyvaultHealth);
				// console.log("📜 app_config - keyvaultHealth.value: ");
				// console.log(keyvaultHealth?.value);
				const frontendSvelteClientId = await client.getSecret('frontend-svelte-client-id');
				const frontendSvelteClientSecret = await client.getSecret('frontend-svelte-client-secret');
				const apiScope = await client.getSecret('api-scope');
				const azTenantId = await client.getSecret('azure-tenant-id');
				const redisSessionPassword = await client.getSecret('redis-session-password');
				const linkedinClientId = await client.getSecret('linkedin-client-id');
				const linkedinClientSecret = await client.getSecret('linkedin-client-secret');
				this.keyvault_health = keyvaultHealth?.value;
				this.backend_host = backend_host?.value || '';
				this.backend_origin = `http://${this.backend_host}:80`;
				this.backend_fqdn = backend_fqdn?.value || '';
				// this.backend_host = backend_host;
				this.frontend_svelte_client_id = frontendSvelteClientId?.value || '';
				this.frontend_svelte_client_secret = frontendSvelteClientSecret?.value || '';
				this.api_scope = apiScope?.value || '';
				this.api_scope_default = `api://${apiScope?.value}/.default`;
				// console.log("📜 app_config - keyvault - api-scope:");
				// console.log(this.api_scope);
				// console.log("📜 app_config - keyvault - api-scope-default:");
				// console.log(this.api_scope_default);
				this.az_authority = `https://login.microsoftonline.com/${azTenantId?.value}`;
				this.az_logout_uri = `https://login.microsoftonline.com/${azTenantId?.value}/oauth2/v2.0/logout`;
				this.encryption = await loadKeyVaultEncryptionKeyring(client);
				this.redis_session_password = redisSessionPassword?.value || '';
				this.linkedin_client_id = linkedinClientId?.value || '';
				this.linkedin_client_secret = linkedinClientSecret?.value || '';
				// TBD: remove authentication_cookie_options - the session-id is now transferred inside state of OAuth-flow?
				// this.authentication_cookie_options = {
				// 	httpOnly: true,
				// 	sameSite: 'none',
				// 	secure: true,
				// 	maxAge: this.authentication_timeout
				// };
				this.session_cookie_options = {
					httpOnly: true,
					sameSite: 'lax',
					secure: true,
					maxAge: this.session_timeout
				};
			} catch (err) {
				console.error('🥞 app_config - server - updateValues - failed');
				throw err;
				// throw new Error("Could not get configuration values from Keyvault");
			}
		} else {
			console.log('📜 app_config - process.env.AZ_KEYVAULT_HOST not set');
			this.keyvault_health = process.env.KEYVAULT_HEALTH;
			this.backend_host = process.env.BACKEND_HOST || '';
			this.backend_origin = `http://${process.env.BACKEND_HOST}:80`;
			this.backend_fqdn = `${process.env.BACKEND_FQDN}`;
			this.frontend_svelte_client_id = process.env.FRONTEND_SVELTE_CLIENT_ID || '';
			this.frontend_svelte_client_secret = process.env.FRONTEND_SVELTE_CLIENT_SECRET || '';
			this.api_scope = process.env.API_SCOPE || '';
			this.api_scope_default = `api://${process.env.API_SCOPE}/.default`;
			this.az_authority = `https://login.microsoftonline.com/${process.env.AZURE_TENANT_ID}`;
			this.az_logout_uri = `https://login.microsoftonline.com/${process.env.AZURE_TENANT_ID}/oauth2/v2.0/logout`;
			this.encryption = loadLocalEncryptionKeyring();
			this.redis_session_password = process.env.REDIS_SESSION_PASSWORD || '';
			this.linkedin_client_id = process.env.LINKEDIN_CLIENT_ID || '';
			this.linkedin_client_secret = process.env.LINKEDIN_CLIENT_SECRET || '';
			// TBD: remove authentication_cookie_options - the session-id is now transferred inside state of OAuth-flow!
			// this.authentication_cookie_options = {
			// 	httpOnly: true,
			// 	sameSite: 'lax',
			// 	secure: false,
			// 	maxAge: this.authentication_timeout
			// };
			this.session_cookie_options = {
				httpOnly: true,
				sameSite: 'lax',
				secure: false,
				maxAge: this.session_timeout
			};
		}
	}
}

// export const app_config = async () => {
// 	const configuration: Configuration = {
// 		api_scope: '',
// 		frontend_svelte_client_id: '',
// 		frontend_svelte_client_secret: '',
// 		az_authority: '',
// 		backend_host: process.env.BACKEND_HOST,
// 		backend_origin: `http://${process.env.BACKEND_HOST}:80`,
// 		ms_graph_base_uri: 'https://graph.microsoft.com/v1.0',
// 		redis_host: process.env.REDIS_HOST,
// 		redis_port: process.env.REDIS_PORT,
// 		redis_session_db: process.env.REDIS_SESSION_DB,
// 		redis_password: ''
// 	}
// 	// It seems that containerapps don't allow env-variables starting with AZURE_
// 	// Apparently that's a reserved namespace. So here AZ_ is used instead.
// 	if (process.env.AZ_KEYVAULT_HOST) {
// 		console.log("app_config - process.env.AZ_KEYVAULT_HOST: ");
// 		console.log(process.env.AZ_KEYVAULT_HOST);
// 		const credential = new ManagedIdentityCredential();
// 		const client = new SecretClient(process.env.AZ_KEYVAULT_HOST, credential);
// 		const keyvaultHealth = await client.getSecret('keyvault-health');
// 		console.log("app_config - keyvaultHealth: ");
// 		console.log(keyvaultHealth);
// 		console.log("app_config - keyvaultHealth.value: ");
// 		console.log(keyvaultHealth.value);
// 		const frontendSvelteClientId = await client.getSecret('app-reg-client-id');
// 		const frontendSvelteClientSecret = await client.getSecret('app-client-secret');
// 		const apiScope = await client.getSecret('api-scope');
// 		const az_tenant_id = await client.getSecret('azure_tenant_id');
// 		const redisPassword = await client.getSecret('redis-password');
// 		configuration.keyvault_health = keyvaultHealth.value;
// 		configuration.frontend_svelte_client_id = frontendSvelteClientId.value || '';
// 		configuration.frontend_svelte_client_secret = frontendSvelteClientSecret.value || '';
// 		configuration.api_scope = apiScope.value || '';
// 		configuration.az_authority = `https://login.microsoftonline.com/${az_tenant_id.value}`,
// 		configuration.redis_session_password = redisSessionPassword.value || '';
// 	}
// 	else {
// 		console.log("app_config - process.env.AZ_KEYVAULT_HOST not set");
// 		configuration.keyvault_health = process.env.KEYVAULT_HEALTH;
// 		configuration.frontend_svelte_client_id = process.env.FRONTEND_SVELTE_CLIENT_ID;
// 		configuration.frontend_svelte_client_secret = process.env.FRONTEND_SVELTE_CLIENT_SECRET;
// 		configuration.api_scope = process.env.API_SCOPE;
// 		configuration.redis_password = process.env.REDIS_PASSWORD;
// 	};
// return configuration;
// };

console.log('👍 📜 lib -server - config.ts - end ');
