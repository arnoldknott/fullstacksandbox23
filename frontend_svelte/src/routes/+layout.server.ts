import { app_config } from '$lib/server/config';
import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ( ) => {
	const configuration =  await app_config()
  // console.log("login - server - configuration");
  // console.log(configuration)
  try {
    const azure_authority = configuration.azure_authority;
    const app_reg_client_id = configuration.app_reg_client_id;
    return { authority: azure_authority, client_id: app_reg_client_id };
  }
  catch (err) {
    console.error(err);
    throw error(404, 'App configuration unavailable');
  }

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
