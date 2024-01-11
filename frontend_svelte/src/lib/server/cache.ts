import { createClient, type RedisClientType } from "redis";
// import {} from @types/redis
import type { Session } from "$lib/types";
// import { app_config } from "./config";
import { building } from "$app/environment"
import AppConfig from './config';

const appConfig = await AppConfig.getInstance();

const sessionTimeOut = 60*5// TBD: this is 5 minutes only - set to three weeks or so for production!
const connectionString = `redis://default:${appConfig.redis_password}@${appConfig.redis_host}:${appConfig.redis_port}`;

// let redisClient: RedisClientType | null = null;
let redisClient: RedisClientType | null = null;
if ( !building) { 
  try{
    redisClient = createClient({url: `${connectionString}/${appConfig.redis_session_db}`})
    await redisClient.connect()
  } catch (err) {
    console.error("🥞 cache - server - createRedisClient - createClient failed");
    // consider let that error bubble up to the caller - in prod a failed redis connection should be fatal!
    // the application needs to restart in its container!
    console.error(err);
  }
}

process.on("exit", () => redisClient?.quit());


// TBDD: should not be necessary any more - the client should keep existing - just needs to be reconnected!
const createRedisClient = async () => {
  if (!redisClient?.isOpen){
    // const configuration = await app_config();
    // const appConfig = await AppConfig.getInstance();
    // console.log("🥞 cache - server - createRedisClient - appConfig.redis_password: ");
    // console.log(appConfig.redis_password.substring(0, 3) + "***");
    // console.log("🥞 cache - server - createRedisClient - appConfig.redis_host: ");
    // console.log(appConfig.redis_host);
    // console.log("🥞 cache - server - createRedisClient - appConfig.redis_port: ");
    // console.log(appConfig.redis_port);
    // console.log("🥞 cache - server - createRedisClient - appConfig.redis_session_db: ");
    // console.log(appConfig.redis_session_db);

    // const connectionString = `redis://default:${appConfig.redis_password}@${appConfig.redis_host}:${appConfig.redis_port}`;

    try{
      redisClient = createClient({
        url: `${connectionString}/${appConfig.redis_session_db}`,
      });
      await redisClient.connect()
    } catch (err) {
      console.error("🥞 cache - server - createRedisClient - createClient failed");
      console.error(err);
      // throw err
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
    console.log("🥞 cache - server - setSession - NEW redisClient");
    console.log(redisClient);
    console.log("🥞 cache - server - setSession - NEW redisClient.isOpen");
    console.log(redisClient?.isOpen);
  }
  console.log("🥞 cache - server - setSession - sessionData.account.localAccountId");
  console.log(sessionData.account.localAccountId);
  const authDataString = JSON.stringify(sessionData);
  console.log("🥞 cache - server - setSession - authDataString");
  console.log(authDataString);
  try{
    console.log("🥞 cache - server - setSession");
    if (!redisClient){
      throw new Error("🥞 cache - server - setSession - redisClient not initialized");
    }
    console.log("🥞 cache - server - setSession - path");
    console.log(path);
    const setStatus = await redisClient?.json.set(sessionId, ".", "teststring");
    // const setStatus = await redisClient.json.set(sessionId, path, authDataString);
    // statusPromise?.catch((err) => {
    //   console.error("🥞 cache - server - setSession - redisClient?.json.set failed");
    //   console.error(err);
    //   // throw err
    // })
    // const setStatus = await statusPromise;
    console.log("🥞 cache - server - setSession - sessionId set");
    await redisClient?.expire(sessionId, sessionTimeOut)
    console.log("🥞 cache - server - setSession - sessionId expired");
    return setStatus === 'OK' ? true : false;
  } catch (err) {
    console.error("🥞 cache - server - setSession - redisClient?.json.set failed");
    console.error(err);
    return false;
    // throw err
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
    console.error(err);
    // throw err
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
    // throw new Error('Session ID is null');
  }
  try{
    await redisClient?.expire(sessionId, sessionTimeOut);
  } catch (err) {
    console.error("🥞 cache - server - updateSessionExpiry - redisClient?.expire failed");
    console.error(err);
    // throw err
  }

  // await useSessionClient(async function(this: RedisClientType) {
  //   await this.expire(sessionId, sessionTimeOut);
  // });
}

// try {
//   await createRedisClient()
// } catch (err) {
//   console.error("🥞 cache - server - createRedisClient failed");
//   console.error(err);
// }