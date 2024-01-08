import { error, type RequestHandler } from '@sveltejs/kit';
import { getMicrosoftGraphBlob } from '$lib/server/microsoft_graph';

export const GET: RequestHandler = async ({ locals, setHeaders }): Promise<Response> => { 
  try {
    if (!locals.sessionData) {
      console.error("api - v1 - user - me - picture - server - no session data");
      throw error(401, "No session data!")
    } else {
      const account = locals.sessionData.account;
      const response = await getMicrosoftGraphBlob(account, '/me/photo/$value');


      if (response && response.status === 200) {
        // TBD: remove all this logging - just for debugging purposes!
        // console.log(" api - v1 - user - me - picture - server - response");
        // console.log(response);
        const pictureBlob = await response.blob();
        console.log(" api - v1 - user - me - picture - server - responseFile");
        console.log(pictureBlob);
        const pictureURL = URL.createObjectURL(pictureBlob);
        console.log(" api - v1 - user - me - picture - server - responseURL");
        console.log(pictureURL);
        // remove to here!
        // setHeaders({ 
        //   'Content-Type': response.headers.get('Content-Type')  || 'text/plain',
        //   'Content-Length': response.headers.get('Content-Length') || '0',
        // });
        setHeaders(
          {'Content-Type': 'image/jpeg'},
        )

        return new Response(pictureBlob)
          // {
          //   headers: {
          //     'Content-Type': response.headers.get('Content-Type')  || 'text/plain',
          //     'Content-Length': response.headers.get('Content-Length') || '0',
          //   }
          // }
        // return response;
      } else {
        console.error("api - v1 - user - me - picture - server - getMicrosoftGraph - userProfile - failed");
        console.log("User Picture status code: " + response.status);
      }
    }
  } catch  {
    console.error("api - v1 - user - me - picture - server - GET - failed");
    throw error(500, "Getting user picture from Microsoft Graph failed")
  }
  return new Response("Getting user picture from Microsoft Graph failed");
}