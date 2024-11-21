import type { LayoutServerLoad } from './$types';
import { getAccessToken } from '$lib/server/oauth';
// import { app_config } from '$lib/server/config';
import AppConfig from '$lib/server/config';
import type { Session, BackendAPIConfiguration } from '$lib/types.d.ts';

// const config = await app_config();

const appConfig = await AppConfig.getInstance();

export const load: LayoutServerLoad = async ({ locals, request }) => {
	let loggedIn = false;
	let sessionData: Session | null = null;
	const backendAPIConfiguration: BackendAPIConfiguration = {
		backendFqdn: appConfig.backend_fqdn,
		restApiPath: '/api/v1',
		websocketPath: '/ws/v1',
		socketIOPath: '/socketio/v1'
	};
	if (locals.sessionData) {
		try {
			const accessToken = await getAccessToken(locals.sessionData, ['User.Read']);
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
