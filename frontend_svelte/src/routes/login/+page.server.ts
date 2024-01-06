import MicrosoftOauth from '$lib/server/oauth';
import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ( { url } ) => {
  const oauth = await MicrosoftOauth.create();
	// const client = MicrosoftOauth.getInstance()
  let loginUrl: string
  try {
    loginUrl = await oauth.signIn( url.origin );
    // console.log("login - server - loginUrl");
    // console.log(loginUrl);
  } catch (err) {
    console.error("login - server - sign in redirect failed");
    console.error(err);
    throw err;
  }
  redirect(302, loginUrl);
	// return { keyvaultHealth: configuration.keyvault_health, url: url.toString() };
};



// import { app_config } from '$lib/server/config';
// import { error } from '@sveltejs/kit';
// import type { PageServerLoad } from './$types';

// export const load: PageServerLoad = async ( ) => {
// 	const configuration =  await app_config()
//   // console.log("login - server - configuration");
//   // console.log(configuration)
//   try {
//     const azure_authority = configuration.azure_authority;
//     const app_reg_client_id = configuration.app_reg_client_id;
//     return { authority: azure_authority, client_id: app_reg_client_id };
//   }
//   catch (err) {
//     console.error(err);
//     throw error(404, 'App configuration unavailable');
//   }

// };

// console.log("Hello from routes/login/+page.server.ts");

// import { postBackend, getBackend } from '$lib/backend';
// import { user_store } from '$lib/stores';
// import { error } from '@sveltejs/kit';

// // TBD: add type PageServerLoad here?
// export const actions = {
// 	default: async ({ cookies, request }) => {
// 		const data = await request.formData();
// 		const payloadLogin = {
// 			email: data.get('email')?.toString() || '',
// 			password: data.get('password')?.toString() || ''
// 		};
// 		const accessToken = await postBackend('/api/user/token/', payloadLogin);
// 		let response = {
// 			status: NaN,
// 			body: {},
// 			redirect: ''
// 		};
// 		if (
// 			!accessToken ||
// 			accessToken.token === 'undefined' ||
// 			accessToken.detail === 'Invalid token.'
// 		) {
// 			response = {
// 				status: 401,
// 				body: {
// 					message: 'Unauthorized'
// 				},
// 				redirect: '/login'
// 			};
// 		} else {
// 			const user = await getBackend('/api/user/me/', accessToken.token);
// 			user.loggedIn = true;
// 			user_store.set(user);
// 			cookies.set('accessToken', accessToken.token);
// 			response = {
// 				status: 200,
// 				body: {
// 					message: 'userLoggedIn'
// 				},
// 				redirect: '/dashboard'
// 			};
// 		}
// 		return response;
// 	}
// };
