import { getTokens } from '$lib/server/oauth';
import { setSession } from '$lib/server/cache';
import type { PageServerLoad } from './$types';
import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';
import type { AuthenticationResult } from '@azure/msal-node';


export const load: PageServerLoad = async ( { url, cookies, locals, request } ) => {
  // console.log("callback - server - locals");
  // console.log(locals);
  console.log("callback - server - request");
  console.log(request);

  const userAgent = request.headers.get('user-agent');
  console.log("callback - server - userAgent");
  console.log(userAgent);
  // console.log(JSON.stringify(userAgent?.data, null, 2));
  const referer = request.headers.get('referer');
  console.log("callback - server - referer");
  console.log(referer);
  const connection = request.headers.get('connection');
  console.log("callback - server - connection");
  console.log(connection);
  try {
    // Acquire tokens with the code from Microsoft Identity Platform
    let authenticationResult: AuthenticationResult;
    try {
      const code = url.searchParams.get("code");
      // console.log("callback - server - code");
      // console.log(code);
      authenticationResult = await getTokens( code, url.origin );
      // console.log("callback - server - tokens");
      // console.log(authenticationResult);
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
      const account = authenticationResult.account;
      // TBD: add expiry!
      if (account ){
        await setSession(sessionId, '.', account);
      } else { 
        console.error("Callback - server - Account not found");
        throw new Error("Callback - server - account is null");
      }

    
      // httpOnly and secure are true by default from sveltekit (https://kit.svelte.dev/docs/types#public-types-cookies)
      // secure is disabled for localhost, but enabled for all other domains
      // TBD: add expiry!
      // TBD: consider restricting path to /(protected)?
      cookies.set('session_id', sessionId, {path: '/', httpOnly: true, sameSite: false });//sameSite: 'strict' });
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