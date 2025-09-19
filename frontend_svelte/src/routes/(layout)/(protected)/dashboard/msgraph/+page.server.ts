import type { PageServerLoad } from './$types';
// import AppConfig from '$lib/server/config';
// import { msalAuthProvider } from '$lib/server/oauth';
// import { error } from '@sveltejs/kit';
import type { User as MicrosoftUser } from '@microsoft/microsoft-graph-types';
import { microsoftGraph } from '$lib/server/apis/msgraph';

// const appConfig = await AppConfig.getInstance();

// TBD: add type PageServerLoad here?
export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;

	const meResponse = await microsoftGraph.get(sessionId, '/me');
	const userProfile = await meResponse.json();

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

	// move this functionality into msgraph api class!
	const allUsers: MicrosoftUser[] = [];
	let usersEndpoint: string | null = '/users';
	while (usersEndpoint) {
		const response = await microsoftGraph.get(sessionId, usersEndpoint);
		const data = await response.json();
		allUsers.push(...data.value);
		const nextLink = data['@odata.nextLink'];
		console.log('=== dashboard - identities - msgraph - nextLink ===');
		console.log(nextLink);
		if (nextLink) {
			const relativeLink = nextLink.replace(/^https:\/\/graph\.microsoft\.com\/v1\.0/, '');
			usersEndpoint = relativeLink;
		} else {
			usersEndpoint = null;
		}
	}

	return {
		account: locals.sessionData.microsoftAccount,
		userProfile: userProfile,
		userPicture: userPicture,
		allUsers: allUsers
	};
};
