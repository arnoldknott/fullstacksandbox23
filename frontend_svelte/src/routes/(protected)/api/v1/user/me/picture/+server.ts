import { msalAuthProvider } from '$lib/server/oauth';
import { error, type RequestHandler } from '@sveltejs/kit';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const GET: RequestHandler = async ({ locals, setHeaders, cookies }): Promise<Response> => {
	try {
		const sessionId = cookies.get('session_id');
		if (!sessionId) {
			console.error('api - v1 - user - me - picture - server - no session id');
			throw error(401, 'No session id!');
		}
		const accessToken = await msalAuthProvider.getAccessToken(sessionId, locals.sessionData, ['User.Read']);
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
