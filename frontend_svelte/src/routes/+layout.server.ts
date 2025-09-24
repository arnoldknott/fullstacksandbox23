import type { LayoutServerLoad } from './$types';
import AppConfig from '$lib/server/config';
import type { BackendAPIConfiguration } from '$lib/types.d.ts';
import { SessionStatus } from '$lib/session';
// import { session } from '$lib/stores';
// import type { User as MicrosoftProfile } from "@microsoft/microsoft-graph-types";

// const config = await app_config();

const appConfig = await AppConfig.getInstance();
// console.log('=== layout.server.ts - appConfig ===');
// console.log(appConfig);

export const load: LayoutServerLoad = async ({ locals }) => {
	// let loggedIn = false;
	// let sessionData: Session | null = null;
	const backendAPIConfiguration: BackendAPIConfiguration = {
		backendFqdn: appConfig.backend_fqdn,
		restApiPath: '/api/v1',
		websocketPath: '/ws/v1',
		socketIOPath: '/socketio/v1'
	};
	// let globalClientData = {
	// 	backendAPIConfiguration: backendAPIConfiguration,
	// 	session: undefined
	// };
	// console.log('=== layout.server.ts - load - locals.sessionData ===');
	// console.log(locals.sessionData.loggedIn);
	if (locals.sessionData && locals.sessionData.loggedIn) {
		console.log('=== layout.server.ts - load - locals.sessionData.status ===');
		console.log(locals.sessionData.status);
		const globalClientData = {
			backendAPIConfiguration: backendAPIConfiguration,
			session: {
				loggedIn: locals.sessionData.loggedIn,
				status: locals.sessionData.status,
				microsoftProfile: locals.sessionData.microsoftProfile,
				sessionId: locals.sessionData.sessionId,
				currentUser: locals.sessionData.currentUser
			}
		};
		// console.log('=== layout.server.ts - load - globalClientData ===');
		// console.log(globalClientData);
		return {
			...globalClientData
		};
	} else {
		return {
			backendAPIConfiguration: backendAPIConfiguration
		};
	}

	// console.log('=== layout.server.ts - load - locals ===');
	// console.log(locals);
	// // TBD: remove the logged in aand use the existence of sessionId in locals.sessionData instead!
	// if (locals.sessionData?.loggedIn) {
	// 	try {
	// 		//  This is handled in hooks.server.ts now!
	// 		// const sessionId = cookies.get('session_id');
	// 		const sessionId = locals.sessionData.sessionId;
	// 		if (!sessionId) {
	// 			console.error('api - v1 - user - me - picture - server - no session id');
	// 			throw error(401, 'No session id!');
	// 		}
	// 		const accessToken = await msalAuthProvider.getAccessToken(sessionId, ['User.Read']);
	// 		const response = await fetch(`${appConfig.ms_graph_base_uri}/me`, {
	// 			headers: {
	// 				Authorization: `Bearer ${aimporting the props ccessToken}`
	// 			}
	// 		});
	// 		// loggedIn = true;
	// 		// sessionData = {
	// 		// 	loggedIn: loggedIn,
	// 		// 	userProfile: await response.json(),
	// 		// 	userAgent: request.headers.get('user-agent')
	// 		// };
	// 		// if (!locals.sessionData){
	// 		//   console.error("layout - server - getMicrosoftGraph - userProfile - failed");
	// 		//   redirect(307, "/");
	// 		// } else {
	// 		//   const account = locals.sessionData.account;
	// 		//   const userProfile = await getMicrosoftGraphData(account, '/me');
	// 		//   return {
	// 		//     userProfile: userProfile
	// 		//   };
	// 	} catch {
	// 		console.error('layout - server - getMicrosoftGraph - userProfile - failed');
	// 	}
	// }
	// return {
	// 	body: {
	// 		sessionData: locals.sessionData, // TBD: remove the full session data here and only pass what's necessary, e.g. loggedIn and userProfile
	// 		backendAPIConfiguration: backendAPIConfiguration
	// 	}
	// };
};
