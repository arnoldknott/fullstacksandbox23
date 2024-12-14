import type { PageServerLoad } from './$types';
// import AppConfig from '$lib/server/config';
// import { msalAuthProvider } from '$lib/server/oauth';
// import { error } from '@sveltejs/kit';
import { microsoftGraph } from '$lib/server/apis';

// const appConfig = await AppConfig.getInstance();

// TBD: add type PageServerLoad here?
export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	// const sessionId = cookies.get('session_id');

	// if (!sessionId) {
	// 	console.error('routes - playground - ms_graph_me - page.server - no session id');
	// 	throw error(401, 'No session id!');
	// }
	// const accessToken = await msalAuthProvider.getAccessToken(sessionId, ['User.Read']);
	// const response = await fetch(`${appConfig.ms_graph_base_uri}/me`, {
	// 	headers: {
	// 		Authorization: `Bearer ${accessToken}`
	// 	}
	// });

	const response = await microsoftGraph.get(sessionId, '/me');

	// a way of returning file content from server load function (untested):
	// Read the file
	// const filePath = 'path/to/your/file';
	// const fileBuffer = await fs.readFile(filePath);
	// const arrayBuffer = fileBuffer.buffer;

	// const pictureResponse = await fetch(`${appConfig.ms_graph_base_uri}/me/photo/$value`, {
	// 	headers: {
	// 		Authorization: `Bearer ${accessToken}`
	// 	}
	// });

	const pictureResponse = await microsoftGraph.get(sessionId, '/me/photo/$value');

	const userPictureBlob = await pictureResponse.blob();
	const userPicture = await userPictureBlob.arrayBuffer();

	// // Create the response object
	// const response = {
	// file: arrayBuffer,
	// ...otherData
	// };

	// // Return the response as JSON
	// return json(response);

	// const demo_resource = await get_ms_graph('/me');
	// console.log("demo resource - server - health");
	// console.log(health);
	// if (health === null) {
	// 	return error(404, 'Unavailable');
	// }
	// console.log("Hello from routes/playground/ms_graph_me/+page.server.ts");
	const userProfile = await response.json();

	return {
		account: locals.sessionData.microsoftAccount,
		userProfile: userProfile,
		userPicture: userPicture
	};
};
