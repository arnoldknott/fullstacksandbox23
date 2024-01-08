import { createClient } from "redis";
// import type { RedisClientType } from "@redis/client";
import type { AccountInfo } from '@azure/msal-node';
type RedisGetReturnType = ReturnType<typeof redisClient.json.get>;

import { app_config } from "./config";

const configuration = await app_config()

const connectionString = `redis://default:${configuration.redis_password}@${configuration.redis_host}:${configuration.redis_port}`;

const redisClient = createClient({
  url: `${connectionString}/${configuration.redis_session_db}`,
});

// console.log("Hello from $lib/server/cache.ts");

const useSessionClient = async <T = void>(callback: (...args: unknown[]) => Promise<T>, ...args: unknown[]) => {
  // Connect to the Redis session client
  await redisClient.connect();

  try {
    // Call the callback function with this.redisSession as its this value and args as its arguments
    return await callback.apply(redisClient, args);
  } finally {
    // Disconnect from the Redis session client
    await redisClient.disconnect();
  }
}

  // async setSession( sessionId: string, path: string, tokens: any ) {
  //   await this.useSessionClient(async function(this: typeof redisSession) {
  //     await this.json.set(sessionId, '.', JSON.stringify(tokens));
  //   }, sessionId, '.', JSON.stringify(tokens));
  // }
export const setSession = async (sessionId: string, path: string, authData: AccountInfo): Promise<void> => {
  // console.log("cache - server - setSession - authData");
  // console.log(authData);
  const authDataString = JSON.stringify(authData);
  await useSessionClient(async function(this: typeof redisClient) {
    await this.json.set(sessionId, path, authDataString);
  });
}

export const getSession = async (sessionId: string): Promise<RedisGetReturnType> => {
  return await useSessionClient(async function(this: typeof redisClient) {
    return await this.json.get(sessionId);
  });
}


  // Ver 3 - Type errors
  // async useSessionClient(methodName: string, ...args: any[]) {
  //   // Connect to the Redis session client
  //   await this.redisSession.connect();

  //   try {
  //     // Call the specified method on this.redisSession with args as its arguments
  //     await this.redisSession[methodName](...args);
  //   } finally {
  //     // Disconnect from the Redis session client
  //     await this.redisSession.disconnect();
  //   }
  // }
  // async useSessionClient(methodName: string, ...args: any[]) {
  //   // Connect to the Redis session client
  //   await this.redisSession.connect();

  //   try {
  //     // Call the specified method on this.redisSession with args as its arguments
  //     await (this.redisSession[methodName] as (...args: any[]) => Promise<void>)(...args);
  //   } finally {
  //     // Disconnect from the Redis session client
  //     await this.redisSession.disconnect();
  //   }
  // }
  // async useSessionClient(methodName: string, ...args: any[]) {
  //   // Connect to the Redis session client
  //   await this.redisSession.connect();

  //   try {
  //     // Call the specified method on this.redisSession with args as its arguments
  //     const method = methodName.split('.');
  //     const func = this.redisSession[method[0]][method[1]] as (...args: any[]) => Promise<void>;
  //     await func(...args);
  //   } finally {
  //     // Disconnect from the Redis session client
  //     await this.redisSession.disconnect();
  //   }
  // }
