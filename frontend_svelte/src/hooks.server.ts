/** @type {import('@sveltejs/kit').Handle} */
// import { signIn } from '$lib/server/security';
// import { logCache } from '$lib/server/oauth';
import { getSession, updateSessionExpiry } from '$lib/server/cache';
import type { Session } from '$lib/types';
import type { AccountInfo } from '@azure/msal-node';
import { error, redirect } from '@sveltejs/kit';
import type { app_config } from '$lib/server/config';

const retrieveSession = async (sessionId: string | null): Promise<Session | void > => {
  if(sessionId){
    const session = await getSession(sessionId);
    if(session){
      await updateSessionExpiry(sessionId);
      // console.log("hooks - server - retrieveSession - account");
      // console.log(session.account);
      // console.log("hooks - server - retrieveSession - userAgent");
      // console.log(session.userAgent);
      return session;
    } else {
      console.error("hooks - server - getSession failed");
    }
  }
}

export const handle = async ({ event, resolve }) => {
  // console.log(event);
  // console.log(event.url.origin);
  // console.log(event.route.id);

  const sessionId = event.cookies.get("session_id");

  if(!sessionId && event.route.id?.includes("(protected)") ){
    console.error("hooks - server - access to protected route without session_id");
    redirect (307, "/login");
    // throw error(403, "Access denied")
  } else if (sessionId) {
    const session = await retrieveSession(sessionId);
    if(!session){
      console.error("hooks - server - session expired");
      event.cookies.delete("session_id", {
        path: "/",
        expires: new Date(0),
      });
      console.log("hooks - server - locals after session expired");
      console.log(event.locals);
      redirect(307, "/");
    } else {
      // console.log("hooks - server - session");
      // console.log(session);
      event.locals.sessionData = session;
    }
    // redirect (307, "/");
  }
  // } else {
  //   console.error("hooks - server - getSession failed");
  //   throw new Error("Session not found in Cache");
  // }

  // console.log("hooks - server - logCache");
  // await logCache();

  // try {
  //   await getTokensFromCache()
  //   // console.log("callback - server - tokens");
  //   // console.log(tokens);
  // } catch (err) {
  //   console.error("hooks - server - getTokensFromCache failed");
  //   console.error(err);
  //   throw err;
  // }

  return await resolve(event);
}