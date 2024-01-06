import MicrosoftOauth from '$lib/server/oauth';
import Cache from '$lib/server/cache';
import type { PageServerLoad } from './$types';
import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';
// import { createClient, type RedisClientType } from "redis";
// import { app_config } from "$lib/server/config";

const cache = new Cache();

export const load: PageServerLoad = async ( { url, cookies } ) => {
  const client = MicrosoftOauth.getInstance()
  const code = url.searchParams.get("code");
  // console.log("callback - server - code");
  // console.log(code);
  
  // const configuration =  await app_config()
  // // console.log("callback - server - configuration");
  // // console.log(configuration)
  // const connectionString = `redis://default:${configuration.redis_password}@${configuration.redis_host}:${configuration.redis_port}/${configuration.redis_session_db}`;
  // console.log("callback - server - connectionString");
  // console.log(connectionString);
  // const redis = createClient({url: connectionString});
  // await redis.connect();
  
  try {
    const tokens = await client.getTokens( code, ["User.Read"], url.origin );
    // console.log("callback - server - tokens");
    // console.log(tokens);
    const sessionId = uuidv4();
    console.log("callback - server - sessionId");
    console.log(sessionId);
    // await redis.set(sessionId, JSON.stringify(tokens));// TBD: add expiry?
    // await cache.useSessionClient( async (sessionId, '.', JSON.stringify(tokens) ) => {}, '', '', '' )
    // await cache.useSessionClient(async (sessionId, path, tokens) => {
    //   console.log("callback - server - calling useSessionClient");
    //   console.log(sessionId);
    //   console.log(path);
    //   console.log(tokens);
    // }, sessionId, '.', JSON.stringify(tokens) );
    // await cache.useSessionClient(cache.redisSession.json.set.bind(cache.redisSession), sessionId, '.', JSON.stringify(tokens) );

  
    // WORKS:
    // await cache.useSessionClient(async ( ) => {
    //   await cache.redisSession.json.set( sessionId, '.', JSON.stringify(tokens) );
    // }, sessionId, '.', JSON.stringify(tokens));

    // WORKS as well - Ver2?:
    await cache.useSessionClient(async function(this: typeof cache.redisSession) {
      await this.json.set(sessionId, '.', JSON.stringify(tokens));
    }, sessionId, '.', JSON.stringify(tokens));

      // Use this (the Redis client) and the arguments
      // console.log('Using the client with arguments', arg1, arg2);
    
    // Ver3 - Type Errors in cache.ts?:
    // await cache.useSessionClient('json.set', sessionId, '.', JSON.stringify(tokens));

    // await redis.json.set(sessionId, '.', JSON.stringify(tokens));// TBD: add expiry?
    // httpOnly and secure are true by default from sveltekit (https://kit.svelte.dev/docs/types#public-types-cookies)
    // secure is disabled for localhost, but enabled for all other domains
    // TBD: add expiry
    // TBD: consider restricting path to /(protected)?
    cookies.set('session_id', sessionId, {path: '/', httpOnly: true, sameSite: 'strict' });
    // await redis.disconnect()
  } catch (err) {
    console.error("Acquiring token in callback failed")
    console.log(err);
    throw err;
  }
  redirect(302, '/');
	// return { keyvaultHealth: configuration.keyvault_health, url: url.toString() };
};


// console.log("Implement redirect to the desired page or the default page here in oauth/callback/+page.server.ts");