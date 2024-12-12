// import { msalAuthProvider } from '$lib/server/oauth';
import { error, type RequestHandler } from '@sveltejs/kit';
import AppConfig from '$lib/server/config';
import { microsoftGraph } from '$lib/server/apis';

const appConfig = await AppConfig.getInstance();

export const GET: RequestHandler = async ({ locals, setHeaders }): Promise<Response> => {
	try {
		// // TBD: delete as checks are now implemented in hooks.server.ts - as long as the route is under (protected) the validity of the session is checked!
		// const sessionId = locals.sessionData.sessionId;
		// if (!sessionId) {
		// 	console.error('api - v1 - user - me - picture - server - no session id');
		// 	throw error(401, 'No session id!');
		// }
		// // Validate session ID and get user data
		// const sessionData = locals.sessionData;
		// if (!sessionData || sessionData.sessionId !== sessionId) {
		// 	console.error('api - v1 - user - me - picture - server - invalid session');
		// 	throw error(401, 'Invalid session!');
		// }
		// const accessToken = await msalAuthProvider.getAccessToken(sessionId, ['User.Read']);
		// const response = await fetch(`${appConfig.ms_graph_base_uri}/me/photo/$value`, {
		// 	headers: {
		// 		Authorization: `Bearer ${accessToken}`
		// 	}
		// });

		const sessionId = locals.sessionData.sessionId;
		const response = await microsoftGraph.get(sessionId, '/me/photo/$value');


		if (
			response &&
			response.status === 200 &&
			response.headers.get('Content-Type') === 'image/jpeg'
		) {
			const pictureBlob = await response.blob();
			setHeaders({ 'Content-Type': 'image/jpeg' });
			return new Response(pictureBlob);
		} else {
			console.error('api - v1 - user - me - picture - server - failed');
			console.log('User Picture status code: ' + response.status);
		}
	} catch {
		console.error('api - v1 - user - me - picture - server - GET - failed');
		throw error(500, 'Getting user picture from Microsoft Graph failed');
	}
	return new Response('Getting user picture from Microsoft Graph failed');
};
