/** @type {import('@sveltejs/kit').Handle} */
// import { signIn } from '$lib/server/security';
// import { logCache } from '$lib/server/oauth';
import { error } from '@sveltejs/kit';

export const handle = async ({ event, resolve }) => {
  // console.log(event);
  // console.log(event.url.origin);
  // console.log(event.route.id);

  const session = event.cookies.get("session_id");

  if(!session && event.route.id?.includes("(protected)") ){
    throw error(401, "Access denied")
  }

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

  const response = await resolve(event);
  return response;
}