import { createClient, type RedisClientType } from 'redis';
import { building } from '$app/environment';
import AppConfig from './config';
import { error } from '@sveltejs/kit';

const appConfig = await AppConfig.getInstance();

// type AppRedisClient = ReturnType<typeof createClient>;

const connectionString = `redis://session:${appConfig.redis_session_password}@${appConfig.redis_host}:${appConfig.redis_port}`;
const sessionTimeOut = appConfig.session_timeout;

class RedisCache {
	redisClient: RedisClientType | null;
	private handlersAttached: boolean = false;

	constructor() {
		this.redisClient = this.startClient();
		this.attachEventHandlers();
	}

	private startClient(): RedisClientType | null {
		try {
			const redisClient = createClient({
				url: `${connectionString}/${appConfig.redis_session_db}`,
				socket: {
					host: appConfig.redis_host,
					port: Number(appConfig.redis_port),
					connectTimeout: 60000,
					keepAlive: true,
					keepAliveInitialDelay: 5000,
					reconnectStrategy: (retries) => {
						// Backoff up to 5s; returning a number keeps reconnecting.
						return Math.min(retries * 200, 5000);
					}
				}
			});
			console.log('👍 🥞 cache - server - createRedisClient - redisClient created');
			return redisClient as RedisClientType;
		} catch (err) {
			if (!building) {
				console.error('🔥 🥞 cache - server - createRedisClient - createClient failed');
				console.error(err);
				// Don't crash the Node process; session features will degrade until Redis is reachable.
				return null;
			} else {
				console.warn(
					'👎 🥞 cache - server - createRedisClient - does not need to create during build'
				);
				return null;
			}
		}
	}

	private attachEventHandlers() {
		if (this.handlersAttached || !this.redisClient) return;
		this.handlersAttached = true;

		// IMPORTANT: without an 'error' handler, Node will treat it as an unhandled
		// EventEmitter error and crash the process (which stops the container).
		this.redisClient.on('error', (err) => {
			console.error('🔥 🥞 cache - server - redisClient error');
			// console.error(err);
		});
		this.redisClient.on('reconnecting', () => {
			console.warn('⚠️ 🥞 cache - server - redisClient reconnecting');
		});
		this.redisClient.on('end', () => {
			console.warn('⚠️ 🥞 cache - server - redisClient connection ended');
		});
		this.redisClient.on('ready', () => {
			console.log('👍 🥞 cache - server - redisClient ready');
		});
	}

	// TBD: what about disconnecting?
	private async connectClient(): Promise<boolean> {
		try {
			if (!this.redisClient) return false;
			this.attachEventHandlers();
			await this.redisClient.connect();
			console.log('👍 🥞 cache - server - createRedisClient - redisClient connected');
			return true;
		} catch (error) {
			console.error('🔥 🥞 cache - server - createRedisClient - connectClient failed');
			console.error(error);
			// Don't throw here; callers should treat this as "session store unavailable".
			return false;
		}
	}

	public async provideClient(): Promise<RedisClientType | null> {
		try {
			if (!this.redisClient) {
				if (building) {
					console.warn(
						'👎 🥞 cache - server - provideClient - redisClient not initialized during build'
					);
					return null;
				}
				throw new Error('🔥 🥞 cache - server - provideClient - redisClient not initialized');
			}
			if (!this.redisClient.isOpen) {
				const connected = await this.connectClient();
				if (!connected) return null;
			}
			return this.redisClient;
		} catch (error) {
			if (!building) {
				console.error('🔥 🥞 cache - server - provideClient - failed');
				console.error(error);
				// During runtime, prefer failing the request/operation rather than crashing the container.
				throw error;
			} else {
				console.warn(
					'👎 🥞 cache - server - provideClient - does not need to connect during build'
				);
				return null;
			}
		}
	}

	// TBD: stop the client when the server is stopped!
	public stopClient() {
		this.redisClient?.destroy();
		console.log('👍 🥞 cache - server - stopClient - redisClient disconnected');
		this.redisClient?.close();
		console.log('👍 🥞 cache - server - stopClient - redisClient quit');
	}

	public async setSession(
		sessionId: string,
		path: string,
		data: string,
		timeOut: number = sessionTimeOut
	): Promise<boolean> {
		try {
			const client = await this.provideClient();
			if (!client) return false;

			const setStatus = await client.json.set(`session:${sessionId}`, path, JSON.parse(data));
			await client.expire(`session:${sessionId}`, timeOut);
			return setStatus === 'OK' ? true : false;
		} catch (err) {
			console.error('🔥 🥞 cache - server - setSession - failed');
			console.error(err);
			return false;
		}
	}

	public async getSession(sessionId: string, path: string = '$'): Promise<object> {
		// TBD: should no longer be necessary, as the sessionId is always a string!
		if (!sessionId) {
			console.error('🔥 🥞 cache - server - getSession - sessionId is null');
			throw new Error('Session ID is null');
		}
		try {
			const client = await this.provideClient();
			if (!client) return {};

			const result = await client.json.get(`session:${sessionId}`, { path: path });
			if (Array.isArray(result) && result.length > 0) {
				return result[0] as object;
			} else {
				return {};
			}
		} catch (err) {
			console.error('🔥 🥞 cache - server - getSession - failed');
			console.error(err);
			throw error(404, 'Session not found');
		}
	}

	public async updateSessionExpiry(
		sessionId: string,
		timeOut: number = sessionTimeOut
	): Promise<void> {
		// TBD: should no longer be necessary, as the sessionId is always a string!
		if (!sessionId) {
			console.error('🔥 🥞 cache - server - updateSessionExpiry - sessionId is null');
			throw error(401, 'Session ID is null');
		}
		try {
			const client = await this.provideClient();
			if (!client) return;

			await client.expire(`session:${sessionId}`, timeOut);
		} catch (err) {
			console.error('🔥 🥞 cache - server - updateSessionExpiry - failed');
			console.error(err);
		}
	}

	public async deleteSession(sessionId: string): Promise<void> {
		// TBD: should no longer be necessary, as the sessionId is always a string!
		if (!sessionId) {
			console.error('🔥 🥞 cache - server - deleteSession - sessionId is null');
			throw error(401, 'Session ID is null');
		}
		try {
			const client = await this.provideClient();
			if (!client) return;

			await client.json.del(`session:${sessionId}`);
		} catch (err) {
			console.error('🔥 🥞 cache - server - deleteSession - failed');
			console.error(err);
		}
	}
}

export const redisCache = new RedisCache();

// TBD: consider getting this back in?
// process.on('exit', () => redisCache?.stopClient());

// OLD CODE:

// let redisClient: RedisClientType | null = null;
// export let redisClient: RedisClientType | null = null;
// if (!building) {
// 	try {
// 		// console.log("🥞 cache - server - createRedisClient - redis app config");
// 		// console.log(appConfig.redis_password.substring(0, 3) + "***");
// 		// console.log(appConfig.redis_host);
// 		// console.log(appConfig.redis_port);
// 		// console.log(appConfig.redis_session_db);
// 		redisClient = await createClient({
// 			url: `${connectionString}/${appConfig.redis_session_db}`,
// 			socket: {
// 				host: appConfig.redis_host,
// 				port: Number(appConfig.redis_port),
// 				connectTimeout: 60000
// 			}
// 		});
// 		// console.log("👍 🥞 cache - server - createRedisClient - redisClient created");
// 		// console.log(redisClient);
// 		// await new Promise((resolve) => setTimeout(resolve, 10000))
// 		await redisClient.connect();
// 		console.log('👍 🥞 cache - server - createRedisClient - redisClient connected');
// 	} catch (err) {
// 		console.error('🥞 cache - server - createRedisClient - createClient and connect failed');
// 		// consider let that error bubble up to the caller - in prod a failed redis connection should be fatal!
// 		// the application needs to restart in its container!
// 		console.error(err);
// 	}
// }

// process.on('exit', () => redisClient?.quit());

// TBDD: should not be necessary any more - the client should keep existing - just needs to be reconnected!
// const createRedisClient = async () => {
//   if (!redisClient?.isOpen){
//     // const configuration = await app_config();
//     // const appConfig = await AppConfig.getInstance();

//     const connectionString = `redis://default:${appConfig.redis_password}@${appConfig.redis_host}:${appConfig.redis_port}`;
//     console.log("🥞 cache - server - createRedisClient - connectionString: ");
//     console.log(connectionString.substring(0, 16) + "***...***" + connectionString.substring(connectionString.length - 12));

//     try{
//       redisClient = createClient({
//         url: `${connectionString}/${appConfig.redis_session_db}`,
//       });
//       await redisClient.connect()
//     } catch (err) {
//       console.error("🥞 cache - server - createRedisClient - createClient failed");
//       console.error(err);
//       // throw err
//     }
//   }
//   return redisClient;
// }

// const useSessionClient = async <T = void>(callback: (...args: unknown[]) => Promise<T>, ...args: unknown[]) => {
//   // Check if redisClient exists, if not create it.
//   redisClient ? null : await createRedisClient()
//   // Connect to the Redis session client
//   if (!redisClient){
//     throw new Error("cache - server - useSessionClient - redisClient not initialized");
//   }
//   if(!redisClient.isOpen){
//     await redisClient.connect();
//   }

//   try {
//     // Call the callback function with this.redisSession as its this value and args as its arguments
//     return await callback.apply(redisClient, args);
//   } finally {
//     // Disconnect from the Redis session client
//     if (redisClient.isOpen){
//       await redisClient.disconnect();
//     }
//   }
// }

// export const setSession = async (
// 	sessionId: string,
// 	path: string,
// 	sessionData: Session
// ): Promise<boolean> => {
// 	// console.log("🥞 cache - server - setSession - redisClient");
// 	// console.log(redisClient);
// 	// console.log("🥞 cache - server - setSession - redisClient?.isOpen");
// 	// console.log(redisClient?.isOpen);
// 	if (!redisClient?.isOpen) {
// 		console.log('🥞 cache - server - setSession - redisClient?.isOpen is false');
// 		await redisClient?.connect();
// 		// console.log("🥞 cache - server - setSession - NEW connection redisClient?.isOpen");
// 		// console.log(redisClient?.isOpen);
// 	}
// 	const authDataString = JSON.stringify(sessionData);
// 	try {
// 		console.log('🥞 cache - server - setSession');
// 		if (!redisClient) {
// 			throw new Error('🥞 cache - server - setSession - redisClient not initialized');
// 		}
// 		const setStatus = await redisClient.json.set(sessionId, path, authDataString);
// 		console.log('👍 🥞 cache - server - setSession - sessionId set');
// 		await redisClient?.expire(sessionId, sessionTimeOut);
// 		console.log('👍 🥞 cache - server - setSession - sessionId expiry set');
// 		return setStatus === 'OK' ? true : false;
// 	} catch (err) {
// 		console.error('🥞 cache - server - setSession - redisClient?.json.set failed');
// 		console.error(err);
// 		return false;
// 		// throw err
// 	}
// };

// export const getSession = async (sessionId: string | null): Promise<Session | undefined> => {
// 	if (!redisClient?.isOpen) {
// 		console.log('🥞 cache - server - getSession - redisClient?.isOpen is false');
// 		await redisClient?.connect();
// 		console.log('🥞 cache - server - setSession - NEW connection redisClient?.isOpen');
// 		console.log(redisClient?.isOpen);
// 	}
// 	if (!sessionId) {
// 		console.error('🥞 cache - server - getSession - sessionId is null');
// 		throw new Error('Session ID is null');
// 	}
// 	try {
// 		const result = await redisClient?.json.get(sessionId);
// 		return result == "string" ? (JSON.parse(result) as Session) : undefined;
// 	} catch (err) {
// 		console.error('🥞 cache - server - getSession - redisClient?.json.get failed');
// 		console.error(err);
// 		// throw err
// 	}
// 	// return await useSessionClient(async function(this: RedisClientType) {
// 	//   const result = await this.json.get(sessionId);
// 	//   return JSON.parse(result) as Session;
// 	// });
// };

// export const updateSessionExpiry = async (sessionId: string | null): Promise<void> => {
// 	if (!redisClient?.isOpen) {
// 		console.log('🥞 cache - server - updateSessionExpiry - redisClient?.isOpen is false');
// 		await redisClient?.connect();
// 		console.log('🥞 cache - server - setSession - NEW connection redisClient?.isOpen');
// 		console.log(redisClient?.isOpen);
// 	}
// 	if (!sessionId) {
// 		console.error('🥞 cache - server - updateSessionExpiry - sessionId is null');
// 		throw new Error('Session ID is null');
// 	}
// 	try {
// 		await redisClient?.expire(sessionId, sessionTimeOut);
// 	} catch (err) {
// 		console.error('🥞 cache - server - updateSessionExpiry - redisClient?.expire failed');
// 		console.error(err);
// 		// throw err
// 	}
// };

console.log('👍 🥞 lib - server - cache.ts - end');
