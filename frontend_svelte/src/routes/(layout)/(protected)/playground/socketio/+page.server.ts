import type { PageServerLoad } from './$types';
import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	if (!sessionId) {
		throw new Error('No session id!');
	}
	// TBD: change scope to socketio!
	// Maybe not necessary - backend is doing ti by itself!
	await msalAuthProvider.getAccessToken(sessionId, [`${appConfig.api_scope}/api.read`]);
};
