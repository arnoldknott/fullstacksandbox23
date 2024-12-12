import type { PageServerLoad } from './$types';
import AppConfig from '$lib/server/config';
// import { msalAuthProvider } from '$lib/server/oauth';
// import { error } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ locals }) => {
	// TBD: consider removing the try catch block
	try {
		// const sessionId = locals.sessionData.sessionId;
		// // const sessionId = cookies.get('session_id');
		// if (!sessionId) {
		// 	console.error('routes - demo-resource - page.server - no session id');
		// 	throw error(401, 'No session id!');
		// }
		// const accessToken = await msalAuthProvider.getAccessToken(sessionId, [
		// 	`${appConfig.api_scope}/api.read`
		// ]); // ["https://management.azure.com/user_impersonation"] ["api.read"]  ["User.Read"]
		// // console.log("playground - on-behalf-of - server - load - accessToken");
		// // console.log(accessToken);
		// const response = await fetch(`${appConfig.backend_origin}/api/v1/core/onbehalfof`, {
		// 	headers: {
		// 		Authorization: `Bearer ${accessToken}`
		// 	}
		// });
		const sessionId = locals.sessionData.sessionId;
		const response = await backendAPI.get(sessionId, '/core/onbehalfof');// add scopes = ["https://management.azure.com/user_impersonation"] ["api.read"]  ["User.Read"] ???
		const schema = await response.json();
		return { schema };
	} catch (err) {
		console.error('playground - on-behalf-of - server - load - failed');
		console.error(err);
		throw err;
	}
};

// console.log("Hello from routes/playground/onbehalfof/+page.server.ts");
