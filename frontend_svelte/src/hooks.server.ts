/** @type {import('@sveltejs/kit').Handle} */
// TBD: import to ES6 typescript import
import { redisCache } from '$lib/server/cache';
import type { Session } from '$lib/types'; // or types.d.ts?
import { redirect, type Handle, type HandleFetch } from '@sveltejs/kit';
import { backendAPI } from '$lib/server/apis/backendApi';

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

export const handle: Handle = async ({ event, resolve }) => {
	// Try Authorization header first (for iframe/localStorage flow)
	const authHeader = event.request.headers.get('Authorization');
	// console.log('=== hooks.server.ts - handle - Authorization header ===');
	// console.log(authHeader);
	let sessionId = authHeader?.replace('Bearer ', '');
	// console.log('=== hooks.server.ts - handle - header - sessionId ===');
	// console.log(sessionId);
	// console.log('=== hooks.server.ts - event - cookies ===');
	// console.log(event.request.headers.get('cookie'));
	// console.log('=== hooks.server.ts - event - url ===');
	// console.log(event.url.href);
	if (!sessionId) {
		sessionId = event.cookies.get('session_id');
	}
	// console.log('=== hooks.server.ts - handle - cookie - sessionId ===');
	// console.log(sessionId);
	const session = sessionId ? await getSession(sessionId) : undefined;
	if (session) {
		// console.log('=== hooks.server.ts - handle - session found - sessionId ===');
		// console.log(sessionId);
		event.locals.sessionData = session;
	}
	// else if (sessionId) {
	// 	// Store sessionId even if session not fully loaded yet
	// 	event.locals.sessionData = { sessionId } as any;
	// }

	let redirectTarget = `/login?targetURL=${event.url.href}`;
	try {
		if (event.route.id?.includes('(protected)')) {
			if (event.locals.sessionData.loggedIn !== true) {
				console.error(
					'🔥 🎣 hooks - server - access attempt to protected route with invalid session'
				);
				throw new Error('Invalid session');
			} else {
				if (event.route.id?.includes('(admin)')) {
					console.log('🎣 hooks - server - access to admin route');
					// TBD: refactor to retrieve this information from the session: it's avaliable in currentUser.
					const userResponse = await backendAPI.get(event.locals.sessionData.sessionId, '/user/me');
					const user = await userResponse.json();
					if (!user.azure_token_roles.includes('Admin')) {
						console.error(
							'🔥 🎣 hooks - server - access to admin route failed (user is not admin)'
						);
						redirectTarget = `/`;
						throw new Error('User is not admin');
					}
				}
			}
		}
	} catch {
		console.error(
			'🔥 🎣 hooks - server - access to this protected route failed (potentially session expired):'
		);
		console.log(event.url.href);
		redirect(307, redirectTarget);
	}
	return await resolve(event);
};

// Add this new export
export const handleFetch: HandleFetch = async ({ request, fetch, event }) => {
	// For internal requests, copy session from event if not already in request
	if (request.url.startsWith(event.url.origin)) {
		const authHeader = request.headers.get('authorization');

		// If request doesn't have auth but event has sessionId, add it
		if (!authHeader && event.locals.sessionData?.sessionId) {
			const headers = new Headers(request.headers);
			headers.set('Authorization', `Bearer ${event.locals.sessionData.sessionId}`);
			request = new Request(request, { headers });
		}
	}

	return fetch(request);
};
