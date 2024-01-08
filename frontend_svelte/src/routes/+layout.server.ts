// import { app_config } from '$lib/server/config';
import { error, redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { getMicrosoftGraphData, getMicrosoftGraphBlob } from '$lib/server/microsoft_graph';

export const load: LayoutServerLoad = async ({ locals }) => {// TBD. add types here!
  try {
    if (!locals.sessionData){
      console.error("layout - server - getMicrosoftGraph - userProfile - failed");
      redirect(307, "/");
    } else {
      const account = locals.sessionData.account;
      const userProfile = await getMicrosoftGraphData(account, '/me');
      // console.log("layout - server - userProfile");
      // console.log(userProfile);
      return {
        // TBD move this to another +layout.server.ts in nested layouts, because we don't need this on very response - especially the picture is a lot of data!
        userProfile: userProfile,// this stays here - universal for all pages -> passes from server to client.
        // userPictureBlob: userPicture// this goes to a protected endpoint from where the client can fetch it.
      };
    }
  } catch {
    console.error("layout - server - getMicrosoftGraph - userProfile - failed");
    // throw error(500, "Getting user profile from Microsoft Graph failed")
  }
  // console.log("layout - server - locals");
  // console.log(locals);

  // return { myLayoutVariable: "any settings, that the frontend needs, for example enabling or disabling features" };
};

// console.log("Hello from src/routes/+layout.server.ts");

// import type { LayoutServerLoad } from './$types';
// import { getBackend } from '$lib/backend';
// import type { User } from 'src/types.d.ts';

// export const load: LayoutServerLoad = async ({ cookies }) => {
// 	let user: User = {
// 		loggedIn: false,
// 		email: ''
// 	};
// 	if (cookies.get('accessToken')) {
// 		user = await getBackend('/api/user/me', cookies.get('accessToken'));
// 		user.loggedIn = true;
// 	}
// 	return user;
// };
