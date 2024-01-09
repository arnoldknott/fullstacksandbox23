import { createClient, type RedisClientType } from "redis";
// import {} from @types/redis
import type { Session } from "$lib/types";
import { app_config } from "./config";

const sessionTimeOut = 60*5// TBD: this is 5 minutes only - set to three weeks or so for production!

let redisClient: RedisClientType | null = null

const createRedisClient = async () => {
  if (!redisClient){
    const configuration = await app_config();

    const connectionString = `redis://default:${configuration.redis_password}@${configuration.redis_host}:${configuration.redis_port}`;

    redisClient = createClient({
      url: `${connectionString}/${configuration.redis_session_db}`,
    });
  }
  return redisClient;
}


const useSessionClient = async <T = void>(callback: (...args: unknown[]) => Promise<T>, ...args: unknown[]) => {
  // Check if redisClient exists, if not create it.
  redisClient ? null : await createRedisClient()
  // Connect to the Redis session client
  if (!redisClient){
    throw new Error("cache - server - useSessionClient - redisClient not initialized");
  }
  await redisClient.connect();

  try {
    // Call the callback function with this.redisSession as its this value and args as its arguments
    return await callback.apply(redisClient, args);
  } finally {
    // Disconnect from the Redis session client
    await redisClient.disconnect();
  }
}

export const setSession = async (sessionId: string, path: string, sessionData: Session): Promise<boolean> => {
  const authDataString = JSON.stringify(sessionData);
  const status = await useSessionClient(async function(this: RedisClientType): Promise<string> {
    const result = await this.json.set(sessionId, path, authDataString);
    await this.expire(sessionId, sessionTimeOut)
    return result;
  });
  console.log("cache - server - setSession - status");
  console.log(status);
  return status === 'OK' ? true : false;
}

  export const getSession = async (sessionId: string | null): Promise<Session> => {
  if (!sessionId) {
    console.error("cache - server - getSession - sessionId is null");
    throw new Error('Session ID is null');
  }
  return await useSessionClient(async function(this: RedisClientType) {
    const result = await this.json.get(sessionId);
    return JSON.parse(result) as Session;
  });
}

export const updateSessionExpiry = async (sessionId: string | null ): Promise<void> => {
  if (!sessionId) {
    console.error("cache - server - updateSessionExpiry - sessionId is null");
    throw new Error('Session ID is null');
  }
  await useSessionClient(async function(this: RedisClientType) {
    await this.expire(sessionId, sessionTimeOut);
  });
}