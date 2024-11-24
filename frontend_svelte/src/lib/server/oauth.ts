// import { app_config } from './config';
import AppConfig from './config';
import { redisCache } from './cache';
import type { RedisClientType } from 'redis';
import {
	ConfidentialClientApplication,
	InteractionRequiredAuthError,
	type AuthenticationResult
} from '@azure/msal-node';
import type { Session } from '$lib/types';
import { building } from '$app/environment';
import type { ICachePlugin, ICacheClient, IPartitionManager, TokenCache } from '@azure/msal-node';
import { type AccountInfo, AccountEntity, TokenCacheContext } from '@azure/msal-common';

const appConfig = await AppConfig.getInstance();
// const scopesBackend = [appConfig.api_scope_default]
const scopesBackend = [
	`api://${appConfig.api_scope}/api.read`,
	`api://${appConfig.api_scope}/api.write`
];
const scopesMsGraph = ['User.Read', 'openid', 'profile', 'offline_access'];
const scoepsAzure = ['https://management.azure.com/user_impersonation']; // for onbehalfof workflow

// use the redisClient other cache operations
class RedisClientWrapper implements ICacheClient {
	private redisClient: RedisClientType;

	constructor(redisClient: RedisClientType) {
		this.redisClient = redisClient;
		console.log('👍 🔑 oauth - Authentication - RedisClientWrapper - created!');
	}

	public async get(key: string): Promise<string> {
		console.log('🔑 oauth - Authentication - RedisClientWrapper - get - key: ');
		console.log(key);
		try {
			return (await this.redisClient.get(key)) || '';
		} catch (error) {
			console.log(error);
		}
		return '';
	}

	public async set(key: string, value: string): Promise<string> {
		console.log('🔑 oauth - Authentication - RedisClientWrapper - set - key: ');
		console.log(key);
		console.log('🔑 oauth - Authentication - RedisClientWrapper - set - value: ');
		console.log(value);
		return (await this.redisClient.set(key, value, { EX: 300 })) || '';
	}
}

// change into session from types.d.ts
interface SessionCacheData {
	account: AccountInfo;
	[key: string]: string | AccountInfo;
}

//
class RedisPartitionManager implements IPartitionManager {
	sessionId: string;
	redisClient: RedisClientWrapper;

	constructor(redisClient: RedisClientWrapper, sessionId: string) {
		this.sessionId = sessionId;
		this.redisClient = redisClient;
		console.log('👍 🔑 oauth - Authentication - RedisPartitionManager - created!');
		console.log('🔑 oauth - Authentication - RedisPartitionManager - sessionId: ');
		console.log(sessionId);
	}

	async getKey(): Promise<string> {
		try {
			// removed the sess: prefix here
			const sessionData = await this.redisClient.get(this.sessionId);
			const session = sessionData ? (JSON.parse(sessionData) as SessionCacheData) : null;
			console.log('🔑 oauth - Authentication - RedisPartitionManager - getKey - session: ');
			console.log(session);
			return '12345'; // TBD: return the real sessionId!
			// return session?.account?.homeAccountId || "";
		} catch (error) {
			console.log(error);
		}

		return '';
	}

	async extractKey(accountEntity: AccountEntity): Promise<string> {
		console.log('🔑 oauth - Authentication - RedisPartitionManager - extractKey - accountEntity: ');
		console.log(accountEntity);
		if (Object.prototype.hasOwnProperty.call(accountEntity, 'homeAccountId')) {
			// if (accountEntity.hasOwnProperty('homeAccountId')) {
			return '12345'; // TBD: return the real sessionId!
			// return accountEntity.homeAccountId; // the homeAccountId is the partition key
		} else {
			throw new Error('homeAccountId is not found');
		}
	}
}

export class MicrosoftTokenCache implements ICachePlugin {
	private client: ICacheClient;
	private partitionManager: IPartitionManager;

	constructor(client: ICacheClient, partitionManager: IPartitionManager) {
		this.client = client;
		this.partitionManager = partitionManager;
	}

	public async beforeCacheAccess(cacheContext: TokenCacheContext): Promise<void> {
		console.log('🔑 oauth - Authentication - MicrosoftTokenCache - beforeCacheAccess');
		const partitionKey = await this.partitionManager.getKey();
		const cacheData = await this.client.get(partitionKey);
		cacheContext.tokenCache.deserialize(cacheData);
	}

	public async afterCacheAccess(cacheContext: TokenCacheContext): Promise<void> {
		console.log('🔑 oauth - Authentication - MicrosoftTokenCache - afterCacheAccess');
		if (cacheContext.cacheHasChanged) {
			const kvStore = (cacheContext.tokenCache as TokenCache).getKVStore();
			// const kvStore = cacheContext.tokenCache.getKVStore();
			const accountEntities = Object.values(kvStore).filter((value) =>
				AccountEntity.isAccountEntity(value as object)
			);

			if (accountEntities.length > 0) {
				const accountEntity = accountEntities[0] as AccountEntity;
				// const accountEntity = cacheContext.tokenCache.getAccount();
				const partitionKey = await this.partitionManager.extractKey(accountEntity);

				await this.client.set(partitionKey, cacheContext.tokenCache.serialize());
				if (cacheContext.cacheHasChanged) {
					await this.client.set('12345', cacheContext.tokenCache.serialize()); // deserialize in-memory cache to persistence
				}
			}
		}
	}
}

class MicrosoftAuthenticationProvider {
	private msalCommonConfig;
	private redisClientWrapper: RedisClientWrapper;

	constructor(redisClient: RedisClientType) {
		// constructor() {
		// Common configuration for all users:
		this.msalCommonConfig = {
			auth: {
				clientId: appConfig.app_reg_client_id,
				authority: appConfig.az_authority,
				clientSecret: appConfig.app_client_secret,
				scopes: [...scopesBackend, ...scopesMsGraph]
			}
		};
		console.log('👍 🔑 oauth - Authentication - Configuration for MsalConfClient - created!');
		this.redisClientWrapper = new RedisClientWrapper(redisClient);
	}

	// add sessionId as parameter
	private createMsalConfClient(): ConfidentialClientApplication {
		try {
			const sessionId = '12345'; // TBD: remove and pass as argument instead!
			// add the cachePlugin to the configuration:
			// instance of MicrosoftTokenCache with the RedisClientWrapper and RedisPartitionManager,
			// where RedisPartitionManager is initialized with the sessionId - so per user only!

			// remove this log, when the redisClientWrapper is used elsewhere
			// console.log('👍 🔑 oauth - Authentication - MsalConfClient - createMsalConfClient - redisClientWrapper');
			// console.log(this.redisClientWrapper);

			const partitionManager = new RedisPartitionManager(this.redisClientWrapper, sessionId);

			const tokenCache = new MicrosoftTokenCache(this.redisClientWrapper, partitionManager);
			const msalUserSessionSpecificConfig = {
				...this.msalCommonConfig,
				cache: { cachePlugin: tokenCache }
			};
			const msalConfClient = new ConfidentialClientApplication(msalUserSessionSpecificConfig);
			console.log('👍 🔑 oauth - Authentication - MsalConfClient - created!');
			// console.log("🔑 oauth - Authentication - getAccessToken - msalConfClient: ");
			// console.log(msalConfClient);
			return msalConfClient;
		} catch (error) {
			console.error('🔥 🔑 oauth - Authentication - MsalConfClient - createMsalConfClient failed');
			console.log(error);
			throw new Error(
				'🔥 🔑 oauth - Authentication - MsalConfClient - createMsalConfClient failed ' + error
			);
		}
	}

	public async signIn(
		origin: string,
		scopes: string[] = [...scopesBackend, ...scopesMsGraph, ...scoepsAzure]
	): Promise<string> {
		try {
			// pass the sessionId to the createMsalConfClient method
			const msalConfClient = this.createMsalConfClient();
			const authCodeUrlParameters = {
				scopes: scopes,
				redirectUri: `${origin}/oauth/callback`
			};
			// let  authCodeUrl: string;
			const authCodeUrl = await msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
			return authCodeUrl;
		} catch (error) {
			console.error('🔥 🔑 oauth - Authentication - signIn failed');
			console.error(error);
			throw error;
		}
	}

	public async authenticateWithCode(
		code: string | null,
		origin: string,
		scopes: string[] = scopesMsGraph
	): Promise<AuthenticationResult> {
		if (!code) {
			throw new Error('🔥 🔑 oauth - GetAccessToken failed - no code');
		}
		try {
			// pass the sessionId to the createMsalConfClient method
			const msalConfClient = this.createMsalConfClient();
			await msalConfClient.getTokenCache().getAllAccounts(); // required for triggering beforeCacheACcess
			const response = await msalConfClient.acquireTokenByCode({
				code: code,
				scopes: scopes,
				redirectUri: `${origin}/oauth/callback`
			});
			console.log('🔑 oauth - Authentication - authenticateWithCode - response: ');
			console.log(response);
			// const tokenCache = msalConfClient.getTokenCache();
			// const accounts = await tokenCache.getAllAccounts();
			return response;
		} catch (error) {
			console.error('🔥 🔑 oauth - GetAccessToken failed');
			console.error(error);
			throw error;
		}
	}

	public async getAccessToken(
		sessionData: Session,
		scopes: string[] = [appConfig.api_scope_default]
	): Promise<string> {
		try {
			// pass the sessionId to the createMsalConfClient method
			const msalConfClient = this.createMsalConfClient();
			// const tokenCache = msalConfClient.getTokenCache();
			// console.log("🔑 oauth - Authentication - getAccessToken - tokenCache: ");
			// console.log(tokenCache);
			// const accounts = await tokenCache.getAllAccounts();
			// console.log("🔑 oauth - Authentication - getAccessToken - allAccounts: ")
			// console.log(accounts);
			// console.log("🔑 oauth - Authentication - getAccessToken - sessionData: ");
			// console.log(sessionData);
			const account = sessionData.userProfile;
			// console.log("🔑 oauth - Authentication - getAccessToken - account: ")
			// console.log(account);
			await msalConfClient.getTokenCache().getAllAccounts(); // required for triggering beforeCacheACcess
			const response = await msalConfClient.acquireTokenSilent({
				scopes: scopes,
				account: account
			});
			// console.log("🔑 oauth - Authentication - getAccessToken - response: ")
			// console.log(response);
			const accessToken = response.accessToken;
			return accessToken;
		} catch (error) {
			if (error instanceof InteractionRequiredAuthError) {
				console.warn('👎 🔑 oauth - GetAccessToken silent failed - sign in again!');
				console.warn(error);
				// TBD: implement redirect to sign in!
				return '';
			} else {
				console.error('🔥 🔑 oauth - GetAccessToken failed');
				console.error(error);
				throw error;
			}
		}
	}
}

// let microsoftAuthenticationProvider: MicrosoftAuthenticationProvider | null = null;

// if (!building) {
// 	if(!redisCache) {
// 		throw new Error('🔑🔥 oauth - Authentication - redisCache not initialized')
// 		};
// 	const redisClient = await redisCache.provideClient();
// 	microsoftAuthenticationProvider = new MicrosoftAuthenticationProvider(redisClient);
// }

// export const signIn = microsoftAuthenticationProvider?.signIn;
// export const authenticateWithCode = microsoftAuthenticationProvider?.authenticateWithCode;
// export const getAccessToken = microsoftAuthenticationProvider?.getAccessToken;

// export const signIn = msalAuthProvider.signIn;
// export const authenticateWithCode = msalAuthProvider.authenticateWithCode;
// export const getAccessToken = msalAuthProvider.getAccessToken;

if (!redisCache) {
	throw new Error('🔑🔥 oauth - Authentication - redisCache not initialized');
}
const redisClient = !building ? await redisCache.provideClient() : ({} as RedisClientType);
export const msalAuthProvider = new MicrosoftAuthenticationProvider(redisClient);

/// OLD CODE:

// let msalConfClient: ConfidentialClientApplication | null = null;

// // construct a user consent urL: https://login.microsoftonline.com/{tenant-id}/authorize?client_id={client-id}
// // https://login.microsoftonline.com/<tenant-id-here>/v2.0/authorize?client_id=<client-id-here>&scope=<scope-here>&redirect_uri=http%3A%2F%2Flocalhost%2Foauth%2Fcallback
// const createMsalConfClient = async () => {
// 	if (!msalConfClient) {
// 		// const configuration = await app_config();
// 		// const appConfig = await AppConfig.getInstance();
// 		// console.log(appConfig.keyvault_health)

// 		const msalConfig = {
// 			auth: {
// 				clientId: appConfig.app_reg_client_id,
// 				authority: appConfig.az_authority,
// 				clientSecret: appConfig.app_client_secret,
// 				scopes: [...scopesBackend, ...scopesMsGraph]
// 				/***********************************************************************************************************************************
// 				Configure persisting the cache to Redis - as soon as Redis is encrypted!
// 				https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/dev/lib/msal-node/docs/caching.md#persistent-cache
// 				Example of implementation of on-behalf-of-with-distributed-cache:
// 				https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/samples/msal-node-samples/auth-code-distributed-cache
// 				implementation of on-behalf-of-with-distributed-cache:
// 				https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/samples/msal-node-samples/on-behalf-of-distributed-cache
// 				implementation of on-behalf-of:
// 				https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/samples/msal-node-samples/on-behalf-of
// 				But not strictly necessary: right now the cache is in a protected network.
// 				***********************************************************************************************************************************/
// 			},
// 			// cache: {
// 			// 	cachePlugin: new MicrosoftTokenCache(
// 			// 		redisClientWrapper,
// 			// 		new RedisPartitionManager(redisClientWrapper, sessionId)
// 			// 	)
// 			// }
// 		};

// 		msalConfClient = new ConfidentialClientApplication(msalConfig);
// 		console.log('🔑👍oauth - Authentication - MsalConfClient - created!');
// 		// TBD: remove cache clearing: debugging ony
// 		// msalConfClient.clearCache()
// 		// console.log("🔑🔥oauth - Authentication - MsalConfClient - cacheCleared!");
// 	}
// 	return msalConfClient;
// };

// if (!building) {
// 	try {
// 		await createMsalConfClient();
// 	} catch (err) {
// 		console.error('🔑🔥 oauth - getTokens - msalConfClient could not created');
// 		throw err;
// 	}
// }

// const checkMsalConfClient = async () => {
// 	if (!msalConfClient) {
// 		try {
// 			await createMsalConfClient();
// 		} catch (err) {
// 			console.error('🔑🔥 oauth - getTokens - msalConfClient could not created');
// 			throw err;
// 		}
// 	}
// 	if (!msalConfClient) {
// 		throw new Error('🔑🔥 oauth - getTokens failed - msalConfClient not initialized');
// 	}
// 	return msalConfClient;
// };

// export const signIn = async (
// 	origin: string,
// 	scopes: string[] = [...scopesBackend, ...scopesMsGraph, ...scoepsAzure]
// ): Promise<string> => {
// 	// Check if msalClient exists on very first login, if not create it.
// 	// const appConfig = AppConfig.getInstance();
// 	// console.log("oauth - Authentication - signIn - appConfig: ");
// 	// console.log(appConfig.keyvault_health);
// 	if (!msalConfClient) {
// 		await createMsalConfClient();
// 	}
// 	// msalConfClient ? null : await createMsalConfClient();
// 	const authCodeUrlParameters = {
// 		scopes: scopes,
// 		redirectUri: `${origin}/oauth/callback`
// 	};
// 	let authCodeUrl: string;
// 	try {
// 		const msalConfClient = await checkMsalConfClient();
// 		authCodeUrl = await msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
// 	} catch (err) {
// 		console.error('🔑🔥 oauth - Authentication - signIn failed');
// 		console.error(err);
// 		throw err;
// 	}
// 	return authCodeUrl;
// };

// export const authenticateWithCode = async (
// 	code: string | null,
// 	origin: string,
// 	scopes: string[] = scopesMsGraph
// ): Promise<AuthenticationResult> => {
// 	if (!code) {
// 		throw new Error('🔥 oauth - GetAccessToken failed - no code');
// 	}
// 	try {
// 		const msalConfClient = await checkMsalConfClient();
// 		const response = await msalConfClient.acquireTokenByCode({
// 			code: code,
// 			scopes: scopes,
// 			redirectUri: `${origin}/oauth/callback`
// 		});
// 		// const tokenCache = msalConfClient.getTokenCache();
// 		// const accounts = await tokenCache.getAllAccounts();
// 		return response;
// 	} catch (err) {
// 		console.error('🔑🔥 oauth - GetAccessToken failed');
// 		console.error(err);
// 		throw err;
// 	}
// };

// export const getAccessToken = async (
// 	sessionData: Session,
// 	scopes: string[] = [appConfig.api_scope_default]
// ): Promise<string> => {
// 	const msalConfClient = await checkMsalConfClient();
// 	try {
// 		const account = sessionData.userProfile;
// 		const response = await msalConfClient.acquireTokenSilent({
// 			scopes: scopes,
// 			account: account
// 		});
// 		const accessToken = response.accessToken;
// 		return accessToken;
// 	} catch (err) {
// 		console.error('🔑🔥 oauth - GetAccessToken failed');
// 		console.error(err);
// 		throw err;
// 	}
// };

// // // export const getAccessTokenMsGraph = async ( sessionData: Session ): Promise<string> => {
// // //   const accessToken = await getAccessToken(sessionData, ["User.Read"])
// // //   return accessToken
// // //}

// // // export const signOut = async ( ): Promise<void> => {
// // //   // TBD: implement logout
// // //   // try {
// // //   //   const msalConfClient = await  checkMsalConfClient()
// // //   //   // implement logout
// // //   // } catch (err) {
// // //   //   console.error("🔑🔥 oauth - Logout failed: ", err);
// // //   //   throw err
// // //   // }
// // // // }

console.log('👍 🔑 lib - server - oauth.ts - end');
