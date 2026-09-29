import { json, type RequestHandler } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import { redisCache } from '$lib/server/cache';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const POST: RequestHandler = async ({ locals, cookies }) => {
	const sessionId = locals.sessionData?.loggedIn ? locals.sessionData.sessionId : undefined;
	if (!sessionId) return json({ success: false }, { status: 401 });
	try {
		const response = await backendAPI.get(sessionId, '/user/me');
		if (!response.ok) {
			return json({ success: false }, { status: response.status >= 500 ? 503 : 401 });
		}
	} catch {
		return json({ success: false }, { status: 503 });
	}
	const renewal = await redisCache.renewSessionIfNeeded(sessionId);
	if (renewal === 'missing') return json({ success: false }, { status: 401 });
	cookies.set('session_id', sessionId, {
		path: '/',
		...appConfig.session_cookie_options
	});
	return new Response(null, { status: 204 });
};
