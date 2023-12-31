/** @type {import('@sveltejs/kit').Handle} */
// import { signIn } from '$lib/server/security';
import { error } from '@sveltejs/kit';

export const handle = async ({ event, resolve }) => {
  // console.log(event);
  // console.log(event.url.origin);
  // console.log(event.route.id);
  if(event.route.id?.includes("(protected)") ){
    // signIn(event.url.origin);
    // console.log("detected protected route");
    throw error(401, "Access denied")
    // return new Response("Access denied", { status: 401, headers: { Location: "/login" } });
  };
  const response = await resolve(event);
  return response;
}