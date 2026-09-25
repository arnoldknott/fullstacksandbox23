import { isRedirect, json, type RequestHandler } from '@sveltejs/kit';

import { backendAuthProvider } from '$lib/server/apis/backendApi';
import { redisCache } from '$lib/server/cache';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const POST: RequestHandler = async ({ locals, cookies }) => {
	const sessionId = locals.sessionData?.loggedIn ? locals.sessionData.sessionId : undefined;
	if (!sessionId) return json({ success: false }, { status: 401 });
	try {
		await backendAuthProvider.getAccessToken(sessionId, [`${appConfig.api_scope}/api.read`]);
	} catch (error) {
		if (!isRedirect(error)) return json({ success: false }, { status: 503 });
		return json({ success: false }, { status: 401 });
	}
	const renewal = await redisCache.renewSessionIfNeeded(sessionId);
	if (renewal === 'missing') return json({ success: false }, { status: 401 });
	cookies.set('session_id', sessionId, {
		path: '/',
		...appConfig.session_cookie_options
	});
	return new Response(null, { status: 204 });
};
