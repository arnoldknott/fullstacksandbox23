import type { User as MicrosoftProfile } from '@microsoft/microsoft-graph-types';

import { IdentityProvider, preferredIdentityProvider } from '$lib/identityProvider';
import { linkedInAPI } from '$lib/server/apis/linkedin';
import { microsoftGraph } from '$lib/server/apis/msgraph';
import AppConfig from '$lib/server/config';
import { redirectToReauthentication } from '$lib/server/oauth/base';
import { LinkedInReauthenticationRequiredError } from '$lib/server/oauth/linkedin';
import type { LinkedInProfile } from '$lib/types';
import type { BackendAPIConfiguration } from '$lib/types.d.ts';

import type { LayoutServerLoad } from './$types';
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
	// console.log(locals.sessionData?.loggedIn);
	if (locals.sessionData && locals.sessionData.loggedIn) {
		let microsoftProfile: MicrosoftProfile | undefined;
		let linkedinProfile: LinkedInProfile | undefined;
		try {
			if (locals.sessionData.identityProvider === IdentityProvider.MICROSOFT) {
				const response = await microsoftGraph.get(locals.sessionData.sessionId, '/me');
				if (response.ok) microsoftProfile = (await response.json()) as MicrosoftProfile;
			} else if (locals.sessionData.identityProvider === IdentityProvider.LINKEDIN) {
				linkedinProfile = await linkedInAPI.getUserInfo(locals.sessionData.sessionId);
			}
		} catch (error) {
			if (error instanceof LinkedInReauthenticationRequiredError) {
				redirectToReauthentication(
					preferredIdentityProvider(
						locals.sessionData.currentUser ?? {},
						locals.sessionData.identityProvider
					)
				);
			}
			// Resource-profile failure does not invalidate an authenticated application session.
			console.error('layout - server - provider profile retrieval failed');
			console.error(error);
		}
		const globalClientData = {
			backendAPIConfiguration: backendAPIConfiguration,
			session: {
				loggedIn: locals.sessionData.loggedIn,
				status: locals.sessionData.status,
				identityProvider: locals.sessionData.identityProvider,
				microsoftProfile,
				linkedinProfile,
				sessionId: locals.sessionData.sessionId,
				currentUser: locals.sessionData.currentUser
			}
		};
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
