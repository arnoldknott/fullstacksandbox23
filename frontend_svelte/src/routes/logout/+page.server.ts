import { app_config } from '$lib/server/config';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ( ) => {
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

// import type { PageServerLoad } from './$types';

// // export const load: PageServerLoad = async ({ cookies }) => {
// export const load: PageServerLoad = async ({  }) => {
// 	// cookies.delete('accessToken');
// };
