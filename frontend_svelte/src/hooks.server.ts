/** @type {import('@sveltejs/kit').Handle} */
import { redisCache } from '$lib/server/cache';
import type { Session } from '$lib/types'; // or types.d.ts?
import { redirect } from '@sveltejs/kit';

const getSession = async (sessionId: string): Promise<Session | void> => {
	try {
		if (sessionId) {
			const session: Session = (await redisCache.getSession(sessionId)) as Session;
			if (session && session?.loggedIn) {
				return session;
			}
		}
	} catch {
		console.error('🎣 hooks - server - getSession - public access, no user logged in');
	}
};

export const handle = async ({ event, resolve }) => {
	const sessionId = event.cookies.get('session_id');
	const session = sessionId ? await getSession(sessionId) : undefined;
	if (session) {
		event.locals.sessionData = session;
	}

	try {
		if (event.route.id?.includes('(protected)')) {
			if (event.locals.sessionData.loggedIn !== true) {
				console.error(
					'🔥 🎣 hooks - server - access attempt to protected route with invalid session'
				);
				redirect(307, `/login?targetURL=${event.url.href}`);
			} else {
				if (event.route.id?.includes('(admin)')) {
					console.log('🎣 hooks - server - access to admin route');
					// Add check if user is admin in backend here
					// thrown another redirect here, if user is not admin!
				}
			}
		}
	} catch {
		console.error(
			'🔥 🎣 hooks - server - access to this protected route failed (potentially session expired):'
		);
		console.log(event.url.href);
		redirect(307, `/login?targetURL=${event.url.href}`);
	}
	return await resolve(event);
};
