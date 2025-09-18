import { error, type RequestHandler } from '@sveltejs/kit';
import { microsoftGraph } from '$lib/server/apis/msgraph';

export const GET: RequestHandler = async ({ locals, url, setHeaders }): Promise<Response> => {
	try {
		console.log('apiproxies/msgraph/+server.ts - GET - url');

		const sessionId = locals.sessionData.sessionId;
		const endpoint = url.searchParams.get('endpoint');
		if (!endpoint) {
			throw error(400, 'Missing endpoint parameter');
		}
		const response = await microsoftGraph.get(sessionId, endpoint);
		if (
			response &&
			response.status === 200 &&
			response.headers.get('Content-Type') === 'image/jpeg'
		) {
			const pictureBlob = await response.blob();
			setHeaders({ 'Content-Type': 'image/jpeg' });
			return new Response(pictureBlob);
		} else {
			console.error('apiproxies - msgraph - GET - failed');
			console.log('MS Graph status code: ' + response.status);
		}
	} catch {
		console.error('apiproxies - msgraph - GET - failed');
		throw error(500, 'Getting data from Microsoft Graph failed');
	}
	return new Response('Getting data from Microsoft Graph failed');
};
