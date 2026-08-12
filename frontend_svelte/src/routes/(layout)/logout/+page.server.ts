import { redirect } from '@sveltejs/kit';

// import { signOut } from '$lib/server/oauth';
import { redisCache } from '$lib/server/cache';
// import {redirect} from '@sveltejs/kit';
import AppConfig from '$lib/server/config';

import type { PageServerLoad } from './$types';
const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ locals, url, cookies }) => {
	// Handle in layout.server.ts?
	const sessionId = locals.sessionData.sessionId;
	cookies.delete('session_id', {
		path: '/',
		expires: new Date(0)
	});
	if (!sessionId) {
		console.error('🔥 logout - server - missing session_id');
		redirect(307, '/');
	}
	await redisCache.deleteSession(sessionId);
	redirect(307, `${appConfig.az_logout_uri}?post_logout_redirect_uri=${url.origin}/`);
};
