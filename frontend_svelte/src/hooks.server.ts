/** @type {import('@sveltejs/kit').Handle} */
import { getSession, updateSessionExpiry } from '$lib/server/cache';
import type { Session } from '$lib/types';
import { redirect } from '@sveltejs/kit';

const retrieveSession = async (sessionId: string | null): Promise<Session | void > => {
  if(sessionId){
    const session = await getSession(sessionId);
    if(session){
      await updateSessionExpiry(sessionId);
      return session;
    } else {
      console.error("🎣 hooks - server - getSession failed");
    }
  }
}

export const handle = async ({ event, resolve }) => {
  const sessionId = event.cookies.get("session_id");

  if(!sessionId){
    if(event.route.id?.includes("(admin)")){
      console.error("🎣 hooks - server - access attempt to admin route without session_id");
      redirect (307, "/");
    } else if (event.route.id?.includes("(protected)")){
      console.error("🎣 hooks - server - access attempt to protected route without session_id");
      redirect (307, "/");
    }
  } else if (sessionId) {
    const session = await retrieveSession(sessionId);
    if(!session){
      console.error("🎣 hooks - server - session expired");
      event.cookies.delete("session_id", {
        path: "/",
        expires: new Date(0),
      });
      console.log("🎣 hooks - server - locals after session expired");
      console.log(event.locals);
      redirect(307, "/");
    } else {
      event.locals.sessionData = session;
    }
  }
  
  return await resolve(event);
}