import { json, type RequestHandler } from '@sveltejs/kit';
import AppConfig from '$lib/server/config';
import { redisCache } from '$lib/server/cache';

const appConfig = await AppConfig.getInstance();

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { sessionId } = await request.json();

	if (!sessionId) return json({ success: false }, { status: 400 });

	const session = await redisCache.getSession(sessionId);
	if (session && Object.prototype.hasOwnProperty.call(session, 'loggedIn')) {
		return json({ success: false }, { status: 401 });
	}

	cookies.set('session_id', sessionId, {
		path: '/',
		...appConfig.session_cookie_options
	});

	return json({ success: true });
};
