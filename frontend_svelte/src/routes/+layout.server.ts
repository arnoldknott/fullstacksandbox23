import type { LayoutServerLoad } from './$types';
import { msalAuthProvider } from '$lib/server/oauth';
// import { app_config } from '$lib/server/config';
import AppConfig from '$lib/server/config';
import type { Session, BackendAPIConfiguration } from '$lib/types.d.ts';

// const config = await app_config();

const appConfig = await AppConfig.getInstance();
// console.log('=== layout.server.ts - appConfig ===');
// console.log(appConfig);

export const load: LayoutServerLoad = async ({ locals, request, cookies }) => {
	let loggedIn = false;
	let sessionData: Session | null = null;
	const backendAPIConfiguration: BackendAPIConfiguration = {
		backendFqdn: appConfig.backend_fqdn,
		restApiPath: '/api/v1',
		websocketPath: '/ws/v1',
		socketIOPath: '/socketio/v1'
	};
	// console.log('=== layout.server.ts - load - locals ===');
	// console.log(locals);
	// TBD: remove the logged in aand use the existence of sessionId in locals.sessionData instead!
	if (locals.sessionData?.loggedIn) {
		try {
			//  This is handled in hooks.server.ts now!
			// const sessionId = cookies.get('session_id');
			const sessionId = locals.sessionData.sessionId;
			if (!sessionId) {
				console.error('api - v1 - user - me - picture - server - no session id');
				throw Error('No session id!');
			}
			const accessToken = await msalAuthProvider.getAccessToken(sessionId, locals.sessionData, [
				'User.Read'
			]);
			const response = await fetch(`${appConfig.ms_graph_base_uri}/me`, {
				headers: {
					Authorization: `Bearer ${accessToken}`
				}
			});
			loggedIn = true;
			sessionData = {
				loggedIn: loggedIn,
				userProfile: await response.json(),
				userAgent: request.headers.get('user-agent')
			};
			// if (!locals.sessionData){
			//   console.error("layout - server - getMicrosoftGraph - userProfile - failed");
			//   redirect(307, "/");
			// } else {
			//   const account = locals.sessionData.account;
			//   const userProfile = await getMicrosoftGraphData(account, '/me');
			//   return {
			//     userProfile: userProfile
			//   };
		} catch {
			console.error('layout - server - getMicrosoftGraph - userProfile - failed');
		}
	}
	return {
		body: {
			sessionData: sessionData,
			backendAPIConfiguration: backendAPIConfiguration
		}
	};
};
