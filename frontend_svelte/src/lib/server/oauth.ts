// import { app_config } from './config';
import AppConfig from './config';
import { redisCache } from './cache';
import type { RedisClientType } from 'redis';
import {
	ConfidentialClientApplication,
	InteractionRequiredAuthError,
	CryptoProvider,
	type AuthenticationResult
} from '@azure/msal-node';
import { building } from '$app/environment';
import {
	DistributedCachePlugin,
	type ICacheClient,
	type IPartitionManager
} from '@azure/msal-node';
import { type AccountInfo, AccountEntity } from '@azure/msal-common';
import { redirect } from '@sveltejs/kit';

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
		// console.log('👍 🔑 oauth - Authentication - RedisClientWrapper - created!');
	}

	public async set(key: string, value: string): Promise<string> {
		const authSessionData =
			(await this.redisClient.json.set(`msal:${key}`, '.', JSON.parse(value))) || '';

		// TBD: increased expiry time after developing - must be pretty long - maybe match token expiry time?
		if (authSessionData) {
			await this.redisClient.expire(`msal:${key}`, 60 * 60 * 24 * 7); // 7 days - adopt to token expiry time?
		}
		return authSessionData;
	}

	public async get(key: string): Promise<string> {
		try {
			const authSessionData = (await this.redisClient.json.get(`msal:${key}`)) || '';
			return JSON.stringify(authSessionData);
		} catch (error) {
			console.log(error);
		}
		return '';
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
		// console.log('👍 🔑 oauth - Authentication - RedisPartitionManager - created!');
	}

	async getKey(): Promise<string> {
		try {
			// TBD: move to / update in redisCache in $lib/server/cache.ts:
			// const regularRedisClient = await redisCache.provideClient();
			// const sessionData = await regularRedisClient.json.get(this.sessionId);
			const sessionData = await redisCache.getSession(this.sessionId);
			// console.log('🔑 oauth - Authentication - RedisPartitionManager - getKey - sessionData')
			// console.log(sessionData);
			const session = sessionData as SessionCacheData;
			const account = session.microsoftAccount as AccountInfo;
			const partitionKey = account?.homeAccountId || '';
			return partitionKey;
		} catch (error) {
			console.log('Error in getKey() : ', error);
		}
		return '';
	}

	async extractKey(accountEntity: AccountEntity): Promise<string> {
		if (Object.prototype.hasOwnProperty.call(accountEntity, 'homeAccountId')) {
			return accountEntity.homeAccountId; // the homeAccountId is the partition key
		} else {
			throw new Error('homeAccountId is not found');
		}
	}
}

// export class MicrosoftTokenCache implements ICachePlugin {
// 	private client: ICacheClient;
// 	private partitionManager: IPartitionManager;

// 	constructor(client: ICacheClient, partitionManager: IPartitionManager) {
// 		this.client = client;
// 		this.partitionManager = partitionManager;
// 	}

// 	public async beforeCacheAccess(cacheContext: TokenCacheContext): Promise<void> {
// 		console.log('🔑 oauth - Authentication - MicrosoftTokenCache - beforeCacheAccess');
// 		const partitionKey = await this.partitionManager.getKey();
// 		const cacheData = await this.client.get(partitionKey);
// 		// try {
// 		// 	cacheContext.tokenCache.deserialize(cacheData);
// 		// } catch (error) {
// 		// 	console.error('🔑 🔥 Error deserializing cache data:');
// 		// 	console.error(error);
// 		// 	throw error;
// 		// }
// 		// cacheContext.tokenCache.deserialize(cacheData);
// 	}

// 	public async afterCacheAccess(cacheContext: TokenCacheContext): Promise<void> {
// 		console.log('🔑 oauth - Authentication - MicrosoftTokenCache - afterCacheAccess');
// 		if (cacheContext.cacheHasChanged) {
// 			const kvStore = (cacheContext.tokenCache as TokenCache).getKVStore();
// 			// const kvStore = cacheContext.tokenCache.getKVStore();
// 			const accountEntities = Object.values(kvStore).filter((value) =>
// 				AccountEntity.isAccountEntity(value as object)
// 			);

// 			if (accountEntities.length > 0) {
// 				const accountEntity = accountEntities[0] as AccountEntity;
// 				const partitionKey = await this.partitionManager.extractKey(accountEntity);

// 				const serializedCache = cacheContext.tokenCache.serialize();

// 				// await this.client.set(partitionKey, cacheContext.tokenCache.serialize());
// 				await this.client.set(partitionKey, serializedCache);
// 				if (cacheContext.cacheHasChanged) {
// 					await this.client.set(partitionKey, cacheContext.tokenCache.serialize()); // deserialize in-memory cache to persistence
// 				}
// 			}
// 		}
// 	}
// }

class MicrosoftAuthenticationProvider {
	private msalCommonConfig;
	private redisClientWrapper: RedisClientWrapper;
	private cryptoProvider: CryptoProvider;

	constructor(redisClient: RedisClientType) {
		// Common configuration for all users:
		this.msalCommonConfig = {
			auth: {
				clientId: appConfig.app_reg_client_id,
				authority: appConfig.az_authority,
				clientSecret: appConfig.app_client_secret,
				scopes: [...scopesBackend, ...scopesMsGraph]
			}
		};
		this.cryptoProvider = new CryptoProvider();
		// console.log('👍 🔑 oauth - Authentication - Configuration for MsalConfClient - created!');
		this.redisClientWrapper = new RedisClientWrapper(redisClient);
	}

	private createMsalConfClient(sessionId: string): ConfidentialClientApplication {
		try {
			// add the cachePlugin to the configuration:
			// instance of MicrosoftTokenCache with the RedisClientWrapper and RedisPartitionManager,
			// where RedisPartitionManager is initialized with the sessionId - so per user only!

			if (!building) {
				const partitionManager = new RedisPartitionManager(this.redisClientWrapper, sessionId);

				// const tokenCache = new MicrosoftTokenCache(this.redisClientWrapper, partitionManager);
				const tokenCache = new DistributedCachePlugin(this.redisClientWrapper, partitionManager);
				const msalUserSessionSpecificConfig = {
					...this.msalCommonConfig,
					cache: { cachePlugin: tokenCache }
				};
				const msalConfClient = new ConfidentialClientApplication(msalUserSessionSpecificConfig);
				// console.log('👍 🔑 oauth - Authentication - MsalConfClient - created!');
				return msalConfClient;
			} else {
				const msalConfClient = new ConfidentialClientApplication(this.msalCommonConfig);
				console.log(
					'👎 🔑 oauth - Authentication - MsalConfClient - created without Cache (not necessary during build stage)!'
				);
				return msalConfClient;
			}
		} catch (error) {
			console.error('🔥 🔑 oauth - Authentication - MsalConfClient - createMsalConfClient failed');
			console.log(error);
			throw new Error(
				'🔥 🔑 oauth - Authentication - MsalConfClient - createMsalConfClient failed ' + error
			);
		}
	}

	public async signIn(
		sessionId: string,
		origin: string,
		targetUrl: string = '/',
		scopes: string[] = [...scopesBackend, ...scopesMsGraph, ...scoepsAzure]
	): Promise<string> {
		try {
			// console.log('🔑 oauth - Authentication - signIn ');
			const csrfToken = this.cryptoProvider.createNewGuid();
			const state = this.cryptoProvider.base64Encode(
				JSON.stringify({
					csrfToken: csrfToken,
					targetURL: targetUrl
				})
			);
			// const regularRedisClient = await redisCache.provideClient();
			// await regularRedisClient.json.set(sessionId, '$.csrfToken', csrfToken);
			// await redisCache.setSession(sessionId, '$.csrfToken', {"csrfToken": csrfToken}, 60 * 10)
			await redisCache.setSession(sessionId, '$.csrfToken', JSON.stringify(csrfToken), 60 * 10);
			const msalConfClient = this.createMsalConfClient(sessionId);
			// pass the state here as well, so user can get redirected to the correct page after login:
			// for example: https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/7a01aafc1af9aca6d51638204aa942700c0418ca/samples/msal-node-samples/auth-code-distributed-cache/src/AuthProvider.ts#L84
			const authCodeUrlParameters = {
				scopes: scopes,
				redirectUri: `${origin}/oauth/callback`,
				state: state
			};
			const authCodeUrl = await msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
			return authCodeUrl;
		} catch (error) {
			console.error('🔥 🔑 oauth - Authentication - signIn failed');
			console.error(error);
			throw error;
		}
	}

	public async decodeState(sessionId: string, state: string): Promise<string> {
		const stateJSON = JSON.parse(this.cryptoProvider.base64Decode(state));
		// const cachedCsrfToken = (await regularRedisClient.json.get(sessionId, {
		// 	path: '$.csrfToken'
		// })) as string[];
		const cachedCsrfToken = await redisCache.getSession(sessionId, '$.csrfToken');
		if (stateJSON.csrfToken === cachedCsrfToken) {
			return stateJSON.targetURL;
		} else {
			throw new Error('CSRF Token mismatch');
		}

		// 	if (cachedCsrfToken && stateJSON.csrfToken !== cachedCsrfToken[0]) {
		// 		// if (stateJSON.csrfToken !== cachedCsrfToken[0]) {
		// 		throw new Error('CSRF Token mismatch');
		// 		// }
		// 	}

		// }
	}

	public async authenticateWithCode(
		sessionId: string,
		code: string | null,
		origin: string,
		scopes: string[] = scopesMsGraph
	): Promise<AuthenticationResult> {
		if (!code) {
			throw new Error('🔥 🔑 oauth - GetAccessToken failed - no code');
		}
		try {
			// console.log('🔑 oauth - Authentication - authenticateWithCode ');
			const msalConfClient = this.createMsalConfClient(sessionId);
			// Doesn't make sense here - at this time the tokens and the session data is not cached yet in Redis:
			// await msalConfClient.getTokenCache().getAllAccounts(); // required for triggering beforeCacheAccess
			const response = await msalConfClient.acquireTokenByCode({
				code: code,
				scopes: scopes,
				redirectUri: `${origin}/oauth/callback`
			});

			const accountData = response.account ? JSON.parse(JSON.stringify(response.account)) : null;
			await redisCache.setSession(sessionId, '$.loggedIn', JSON.stringify(true));
			await redisCache.setSession(sessionId, '$.microsoftAccount', JSON.stringify(accountData));
			await redisCache.setSession(sessionId, '$.sessionId', JSON.stringify(sessionId));

			// await redisCache.updateSessionExpiry(sessionId, timeOut);

			return response;
		} catch (error) {
			console.error('🔥 🔑 oauth - GetAccessToken failed');
			console.error(error);
			throw error;
		}
	}

	public async getAccessToken(
		sessionId: string,
		scopes: string[] = [appConfig.api_scope_default]
	): Promise<string> {
		try {
			// console.log('🔑 oauth - Authentication - getAccessToken ');
			const msalConfClient = this.createMsalConfClient(sessionId);
			await msalConfClient.getTokenCache().getAllAccounts(); // required for triggering beforeCacheACcess
			// const regularRedisClient = await redisCache.provideClient();
			// // TBD: move to / update in redisCache in $lib/server/cache.ts:
			// const accountResponse = await regularRedisClient.json.get(sessionId, {
			// 	path: '$.microsoftAccount'
			// });
			const account = (await redisCache.getSession(sessionId, '$.microsoftAccount')) as AccountInfo;
			// console.log('🔑 oauth - Authentication - getAccessToken - accountResponse')
			// console.log(account);
			const response = await msalConfClient.acquireTokenSilent({
				scopes: scopes,
				account: account
			});
			const accessToken = response.accessToken;
			return accessToken;

			// if (!accountResponse) {
			// 	console.error('🔥 🔑 oauth - GetAccessToken failed - no account');
			// 	throw new Error();
			// }
			// if (Array.isArray(accountResponse) && accountResponse.length > 0) {
			// 	const account: AccountInfo = accountResponse[0] as unknown as AccountInfo;
			// 	const response = await msalConfClient.acquireTokenSilent({
			// 		scopes: scopes,
			// 		account: account
			// 	});
			// 	const accessToken = response.accessToken;
			// 	return accessToken;
			// } else {
			// 	throw new Error('🔥 🔑 oauth - GetAccessToken failed - accountResponse missing');
			// }
		} catch (error) {
			if (error instanceof InteractionRequiredAuthError) {
				console.warn('👎 🔑 oauth - GetAccessToken silent failed - sign in again!');
				// console.log("===> redirecting to '/login' <===");
				redirect(307, '/login');
			} else {
				console.error('🔥 🔑 oauth - GetAccessToken failed');
				console.error(error);
				throw error;
			}
		}
	}
}

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
