import { getTokens } from '$lib/server/oauth';
import { setSession } from '$lib/server/cache';
import type { PageServerLoad } from './$types';
import { v4 as uuidv4 } from 'uuid';
import { redirect } from '@sveltejs/kit';
import type { AuthenticationResult } from '@azure/msal-node';


export const load: PageServerLoad = async ( { url, cookies, request } ) => {
  // const userAgent = request.headers.get('user-agent');
  // const referer = request.headers.get('referer');
  // const connection = request.headers.get('connection');
  try {
    // Acquire tokens with the code from Microsoft Identity Platform
    let authenticationResult: AuthenticationResult;
    try {
      const code = url.searchParams.get("code");
      authenticationResult = await getTokens( code, url.origin );
    } catch (err) {
      console.error("Callback - server - getTokens failed");
      console.error(err);
      throw err;
    }
    
  
    // Create a session, store authenticationResult in the cache, and set the session cookie
    try {
      const sessionId = uuidv4();
      const account = authenticationResult.account;
      // TBD: add expiry!
      if (account){
        const userAgent = request.headers.get('user-agent');
        const session = {
        account: account,
        userAgent: userAgent || '',
        }
        await setSession(sessionId, '.', session);
      } else { 
        console.error("Callback - server - Account not found");
        throw new Error("Callback - server - account is null");
      }

    
      // httpOnly and secure are true by default from sveltekit (https://kit.svelte.dev/docs/types#public-types-cookies)
      // secure is disabled for localhost, but enabled for all other domains
      // TBD: add expiry!
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
};
