import { createClient } from "redis";
// import type { RedisClientType } from "@redis/client";
import { app_config } from "./config";

const configuration = await app_config()

const connectionString = `redis://default:${configuration.redis_password}@${configuration.redis_host}:${configuration.redis_port}`;

const redisSession = createClient({
  url: `${connectionString}/${configuration.redis_session_db}`,
});

// console.log("Hello from $lib/server/cache.ts");

export default class Cache {
  redisSession!: typeof redisSession;

  constructor() {
    this.redisSession = redisSession;
    // this.redisSession.json.set("foo", ".", JSON.stringify({ bar: "baz" }));
  }

  
  // WORKS:
  // async useSessionClient( callback: ( ...args: any[] ) => Promise<void>, ...args: any[] ) {
  //   await this.redisSession.connect();
  //   // console.log("cache - server - useSessionClient - callback");
  //   // console.log(callback.name);
  //   // console.log(args)
  //   // console.log(typeof callback); // should print 'function'
  //   // console.log(callback instanceof Function); // should print true
  //   // console.log(Array.isArray(args)); // should print true
  //   await callback.apply(this.redisSession, args);
  //   await this.redisSession.disconnect();
  // }

  // WOKRS as well - Ver2?
  // TBD: change unknonw to a RedisClientType or RedisFunction?
  async useSessionClient(callback: (...args: unknown[]) => Promise<void>, ...args: unknown[]) {
    // Connect to the Redis session client
    await this.redisSession.connect();

    try {
      // Call the callback function with this.redisSession as its this value and args as its arguments
      await callback.apply(this.redisSession, args);
    } finally {
      // Disconnect from the Redis session client
      await this.redisSession.disconnect();
    }
  }

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
