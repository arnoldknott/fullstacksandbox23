import { createClient } from "redis";
// import type { RedisClientType } from "@redis/client";
// import type { AccountInfo } from '@azure/msal-node';
type RedisGetReturnType = ReturnType<typeof redisClient.json.get>;
import type { Session } from "$lib/types";

import { app_config } from "./config";

const configuration = await app_config()
const sessionTimeOut = 60*5// TBD: this is 5 minutes only - set to three weeks or so for production!

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
export const setSession = async (sessionId: string, path: string, sessionData: Session): Promise<boolean> => {
  // console.log("cache - server - setSession - authData");
  // console.log(authData);
  const authDataString = JSON.stringify(sessionData);
  // let status: string;
  let status = await useSessionClient(async function(this: typeof redisClient): Promise<string> {
    const result = await this.json.set(sessionId, path, authDataString);
    await this.expire(sessionId, sessionTimeOut)
    return result;
  });
  console.log("cache - server - setSession - status");
  console.log(status);
  return status === 'OK' ? true : false;
}

// export const getSession = async (sessionId: string | null): Promise<RedisGetReturnType> => {
  export const getSession = async (sessionId: string | null): Promise<Session> => {
  if (!sessionId) {
    console.error("cache - server - getSession - sessionId is null");
    throw new Error('Session ID is null');
  }
  return await useSessionClient(async function(this: typeof redisClient) {
    const result = await this.json.get(sessionId);
    return JSON.parse(result) as Session;
  });
}

export const updateSessionExpiry = async (sessionId: string | null ): Promise<void> => {
  if (!sessionId) {
    console.error("cache - server - updateSessionExpiry - sessionId is null");
    throw new Error('Session ID is null');
  }
  await useSessionClient(async function(this: typeof redisClient) {
    await this.expire(sessionId, sessionTimeOut);
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
