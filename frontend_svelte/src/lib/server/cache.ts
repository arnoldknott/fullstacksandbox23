import { createClient, type RedisClientType } from "redis";
// import {} from @types/redis
import type { Session } from "$lib/types";
// import { app_config } from "./config";
import AppConfig from './config';

const sessionTimeOut = 60*5// TBD: this is 5 minutes only - set to three weeks or so for production!

let redisClient: RedisClientType | null = null

process.on("exit", () => redisClient?.quit());

const createRedisClient = async () => {
  if (!redisClient?.isOpen){
    // const configuration = await app_config();
    const appConfig = await AppConfig.getInstance();
    console.log("🥞 cache - server - createRedisClient - appConfig.redis_password: ");
    console.log(appConfig.redis_password.substring(0, 3) + "***");
    console.log("🥞 cache - server - createRedisClient - appConfig.redis_host: ");
    console.log(appConfig.redis_host);
    console.log("🥞 cache - server - createRedisClient - appConfig.redis_port: ");
    console.log(appConfig.redis_port);
    console.log("🥞 cache - server - createRedisClient - appConfig.redis_session_db: ");
    console.log(appConfig.redis_session_db);

    const connectionString = `redis://default:${appConfig.redis_password}@${appConfig.redis_host}:${appConfig.redis_port}`;

    try{
      redisClient = createClient({
        url: `${connectionString}/${appConfig.redis_session_db}`,
      });
      await redisClient.connect()
    } catch (err) {
      console.error("🥞 cache - server - createRedisClient - createClient failed");
      throw err
    }
  }
  return redisClient;
}


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

export const setSession = async (sessionId: string, path: string, sessionData: Session): Promise<boolean> => {
  console.log("🥞 cache - server - setSession - redisClient");
  console.log(redisClient);
  console.log("🥞 cache - server - setSession - redisClient?.isOpen");
  console.log(redisClient?.isOpen);
  if(!redisClient?.isOpen){
    console.log("🥞 cache - server - setSession - redisClient?.isOpen is false");
    redisClient = await createRedisClient();
    console.log("🥞 cache - server - setSession - new redisClient");
    console.log(redisClient);
    console.log("🥞 cache - server - setSession - new redisClient.isOpen");
    console.log(redisClient.isOpen);
  }
  const authDataString = JSON.stringify(sessionData);
  try{
    console.log("🥞 cache - server - setSession");
    const status = await redisClient?.json.set(sessionId, path, authDataString);
    console.log("🥞 cache - server - setSession - sessionId set");
    await redisClient?.expire(sessionId, sessionTimeOut)
    console.log("🥞 cache - server - setSession - sessionId expired");
    return status === 'OK' ? true : false;
  } catch (err) {
    console.error("🥞 cache - server - setSession - redisClient?.json.set failed");
    throw err
  }
  // const status = await useSessionClient(async function(this: RedisClientType): Promise<string> {
  //   const result = await this.json.set(sessionId, path, authDataString);
  //   await this.expire(sessionId, sessionTimeOut)
  //   return result;
  // });
  // console.log("cache - server - setSession - status");
  // console.log(status);
}

  export const getSession = async (sessionId: string | null): Promise<Session | undefined > => {
  if(!redisClient?.isOpen){
    await createRedisClient();
  }
  if (!sessionId) {
    console.error("🥞 cache - server - getSession - sessionId is null");
    throw new Error('Session ID is null');
  }
  try{
    const result = await redisClient?.json.get(sessionId);
    return result ? JSON.parse(result) as Session : undefined;
  } catch (err) {
    console.error("🥞 cache - server - getSession - redisClient?.json.get failed");
    throw err
  }
  // return await useSessionClient(async function(this: RedisClientType) {
  //   const result = await this.json.get(sessionId);
  //   return JSON.parse(result) as Session;
  // });
}

export const updateSessionExpiry = async (sessionId: string | null ): Promise<void> => {
  if(!redisClient?.isOpen){
    await createRedisClient();
  }
  if (!sessionId) {
    console.error("🥞 cache - server - updateSessionExpiry - sessionId is null");
    throw new Error('Session ID is null');
  }
  try{
    await redisClient?.expire(sessionId, sessionTimeOut);
  } catch (err) {
    console.error("🥞 cache - server - updateSessionExpiry - redisClient?.expire failed");
    throw err
  }

  // await useSessionClient(async function(this: RedisClientType) {
  //   await this.expire(sessionId, sessionTimeOut);
  // });
}