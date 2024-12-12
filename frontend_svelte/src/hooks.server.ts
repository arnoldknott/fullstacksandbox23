/** @type {import('@sveltejs/kit').Handle} */
import { redisCache } from '$lib/server/cache';
import type { Session } from '$lib/types'; // or types.d.ts?
import { redirect } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis';

const getSession = async (sessionId: string): Promise<Session | void> => {
	try {
		if (sessionId) {
			const session: Session = (await redisCache.getSession(sessionId)) as Session;
			if (session && session?.loggedIn) {
				return session;
			}
		}
	} catch {
		console.error('🔥 🎣 hooks - server - getSession - public access, no user logged in');
	}
};


export const handle = async ({ event, resolve }) => {
	const sessionId = event.cookies.get('session_id');
	const session = sessionId ? await getSession(sessionId) : undefined;
	if (session) {
		event.locals.sessionData = session;
	}

	let redirectTarget = `/login?targetURL=${event.url.href}`
	try {
		if (event.route.id?.includes('(protected)')) {
			if (event.locals.sessionData.loggedIn !== true) {
				console.error(
					'🔥 🎣 hooks - server - access attempt to protected route with invalid session'
				);
				throw new Error('Invalid session');
				// redirect(307, `/login?targetURL=${event.url.href}`);
			} else {
				if (event.route.id?.includes('(admin)')) {
					console.log('🎣 hooks - server - access to admin route');
					const userResponse = await backendAPI.get(event.locals.sessionData.sessionId, '/user/me');
					const user = await userResponse.json();
					if (!user.azureTokenRoles.includes('Admin')) {
						console.error(
							'🔥 🎣 hooks - server - access to admin route failed (user is not admin)'
						);
						redirectTarget = `/`;
						throw new Error('User is not admin');
						// redirect(307, `/`);
					}
					// Add check if user is admin in backend here
					// thrown another redirect here, if user is not admin!
				}
			}
		}
	} catch (error) {
		console.error(
			'🔥 🎣 hooks - server - access to this protected route failed (potentially session expired):'
		);
		console.log(event.url.href);
		// redirect(307, `/login?targetURL=${event.url.href}`);
		redirect(307, redirectTarget);
	}
	return await resolve(event);
};
