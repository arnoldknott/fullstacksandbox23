// import { app_config } from '$lib/server/config';
import { error, redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { getMicrosoftGraphData, getMicrosoftGraphBlob } from '$lib/server/microsoft_graph';

export const load: LayoutServerLoad = async ({ locals }) => {// TBD. add types here!
  try {
    if (locals.sessionData){
      const account = locals.sessionData.account;
      const userProfile = await getMicrosoftGraphData(account, '/me');
      console.log("layout - server - userProfile");
      console.log(userProfile);
      const userPictureBlob = await getMicrosoftGraphBlob(account, '/me/photo/$value');
      const userPicture = URL.createObjectURL(userPictureBlob);// TBD - do this on the client!!
      console.log("layout - server - pictureUrl");
      console.log(userPicture);
      return {
        // TBD move this to another +layout.server.ts in nested layouts, because we don't need this on very response - especially the picture is a lot of data!
        userProfile: userProfile,
        userPictureBlob: userPicture
      };
    }
  } catch {
    console.error("layout - server - getMicrosoftGraph - userProfile - failed");
    redirect(307, "/");
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
