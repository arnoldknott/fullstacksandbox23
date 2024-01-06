import MicrosoftOauth from '$lib/server/oauth';
import Cache from '$lib/server/cache';
import type { PageServerLoad } from './$types';
import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';
import type { AuthenticationResult } from '@azure/msal-node';


export const load: PageServerLoad = async ( { url, cookies } ) => {
  try {
    // Acquire tokens with the code from Microsoft Identity Platform
    let authenticationResult: AuthenticationResult;
    try {
      const oauth = await MicrosoftOauth.create();
      // const client = MicrosoftOauth.getInstance()
      const code = url.searchParams.get("code");
      // console.log("callback - server - code");
      // console.log(code);
      const azure_scopes = ["User.Read"];
      authenticationResult = await oauth.getTokens( code, azure_scopes, url.origin );
      // console.log("callback - server - tokens");
      // console.log(tokens);
    } catch (err) {
      console.error("Callback - server - getTokens failed");
      console.error(err);
      throw err;
    }
    
  
    // Create a session, store authenticationResult in the cache, and set the session cookie
    try {
      const sessionId = uuidv4();
      // console.log("callback - server - sessionId");
      // console.log(sessionId);

      // TBD: add expiry!
      const cache = new Cache();
      await cache.setSession(sessionId, '.', JSON.stringify(authenticationResult));
    
      // httpOnly and secure are true by default from sveltekit (https://kit.svelte.dev/docs/types#public-types-cookies)
      // secure is disabled for localhost, but enabled for all other domains
      // TBD: add expiry!
      // TBD: consider restricting path to /(protected)?
      cookies.set('session_id', sessionId, {path: '/', httpOnly: true, sameSite: 'strict' });
    } catch (err) {
      console.error("Callback - server - create session failed");
      console.error(err);
      throw err;
    }

  

  } catch (err) {
    console.error("Callback session initialization failed")
    console.log(err);
    throw err;
  }
  redirect(302, '/');
	// return { keyvaultHealth: configuration.keyvault_health, url: url.toString() };
};


// console.log("Implement redirect to the desired page or the default page here in oauth/callback/+page.server.ts");