import { msalAuthProvider } from '$lib/server/oauth';
import { error, type RequestHandler } from '@sveltejs/kit';
import AppConfig from '$lib/server/config';

// TBD move the frontend API to the (plain routes), no need to load the layout browser components here!

const appConfig = await AppConfig.getInstance();

// This is a publically accessible endpoint - so anyone could get to this data without authentication!!!
// TBD: remove! The secured API endpoints are in the backend API. This is just a demo.
// Reconsider: now the session is validated!

export const GET: RequestHandler = async ({ locals, setHeaders }): Promise<Response> => {
	try {
		// const sessionId = cookies.get('session_id');
		const sessionId = locals.sessionData.sessionId;
		if (!sessionId) {
			console.error('api - v1 - user - me - picture - server - no session id');
			throw error(401, 'No session id!');
		}
		// Validate session ID and get user data
		const sessionData = locals.sessionData;
		// console.log('api - v1 - user - me - picture - server - sessionData');
		// console.log(sessionData.sessionId);
		if (!sessionData || sessionData.sessionId !== sessionId) {
			console.error('api - v1 - user - me - picture - server - invalid session');
			throw error(401, 'Invalid session!');
		}
		const accessToken = await msalAuthProvider.getAccessToken(sessionId, ['User.Read']);
		// console.log('api - v1 - user - me - picture - server - accessToken');
		// console.log(accessToken);
		const response = await fetch(`${appConfig.ms_graph_base_uri}/me/photo/$value`, {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		});

		// if (!locals.sessionData) {
		//   console.error("api - v1 - user - me - picture - server - no session data");
		//   throw error(401, "No session data!")
		// } else {
		//   const account = locals.sessionData.account;
		//   const response = await getMicrosoftGraphBlob(account, '/me/photo/$value');

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
