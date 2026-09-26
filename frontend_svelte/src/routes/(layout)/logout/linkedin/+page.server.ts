import { redirect } from '@sveltejs/kit';

import { redisCache } from '$lib/server/cache';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, cookies }) => {
	const sessionId = locals.sessionData.sessionId;
	cookies.delete('session_id', { path: '/', expires: new Date(0) });
	if (sessionId) await redisCache.deleteSession(sessionId);
	redirect(307, '/');
};
