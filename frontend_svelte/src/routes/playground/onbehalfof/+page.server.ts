import type { PageServerLoad } from './$types';
import AppConfig from '$lib/server/config';
import { getAccessToken } from '$lib/server/oauth';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ( {locals} ) => {
	// TBD: consider removing the try catch block
	try {
		const accessToken = await getAccessToken(locals.sessionData, [`${appConfig.api_scope}/api.read`]  );// ["https://management.azure.com/user_impersonation"] ["api.read"] ["User.Read"]
		console.log("playground - on-behalf-of - server - load - accessToken");
		console.log(accessToken);
		const response = await fetch(`${appConfig.backend_origin}/api/v1/core/onbehalfof`, {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		});
		const schema = await response.json();
		return { body: schema };
	} catch (err) {
		console.error('playground - on-behalf-of - server - load - failed');
		console.error(err);
		throw err;
	}
};

// console.log("Hello from routes/playground/onbehalfof/+page.server.ts");