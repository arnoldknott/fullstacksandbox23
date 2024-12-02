/** @type {import('@sveltejs/kit').Handle} */
import { redisCache } from '$lib/server/cache';
import type { Session } from '$lib/types'; // TBD: move to app.d.ts (look at new template from ground up installation)
import { redirect, error } from '@sveltejs/kit';

// const retrieveSession = async (sessionId: string | null): Promise<Session | void> => {
// 	if (sessionId) {
// 		const session = await redisCache.getSession(sessionId);
// 		// console.log('🎣 hooks - server - retrieveSession - session');
// 		// console.log(session);
// 		if (session) {
// 			await redisCache.updateSessionExpiry(sessionId);
// 			return session;
// 		} else {
// 			console.error('🔥 🎣 hooks - server - getSession failed');
// 		}
// 	}
// };

const redirectLogin = (tagetUrl: string) => {
	redirect(307, `/login?targetURL=${tagetUrl}`);
};

const getSession = async (sessionId: string): Promise<Session | void> => {
	try {
		// console.log('🎣 hooks - server - sessionId')
		// console.log(sessionId);
		if (sessionId) {
			const session: Session = (await redisCache.getSession(sessionId)) as Session;
			// console.log('🎣 hooks - server - session');
			// console.log(session);
			if (session && session?.loggedIn) {
				return session;
			}
		}
	} catch {
		console.error('🎣 hooks - server - getSession - public access, no user logged in');
	}
};

export const handle = async ({ event, resolve }) => {
	try {
		// console.log('🎣 hooks - server - access to route - event.url.href - before session check:')
		// console.log(event.url.href);
		if (event.cookies) {
			const sessionId = event.cookies.get('session_id');
			// console.log('🎣 hooks - server - sessionId')
			// console.log(sessionId);
			const session = sessionId ? await getSession(sessionId) : undefined;
			// console.log('🎣 hooks - server - session')
			// console.log(session);
			if (session) {
				// console.log('🎣 hooks - server - session.loggedIn')
				// console.log(session.loggedIn);
				event.locals.sessionData = session;
			}
		}

		console.log('🎣 hooks - server - access to route - event.url.href - after session check:');
		console.log(event.url.href);
		if (event.route.id?.includes('(protected)')) {
			// console.log('🎣 hooks - server - access to protected route:');
			// console.log(event.url.href);
			if (event.locals.sessionData.loggedIn !== true) {
				console.error(
					'🔥 🎣 hooks - server - access attempt to protected route with invalid session'
				);
				redirectLogin(event.url.href);
			} else {
				if (event.route.id?.includes('(admin)')) {
					console.log('🎣 hooks - server - access to admin route');
					// Add check if user is admin in backend here
					// thrown another redirect here, if user is not admin!
				}
			}
			// console.log('🎣 hooks - server - access to route - event:')
			// console.log(event);
		}
		return await resolve(event);
	} catch (err) {
		console.error('🔥 🎣 hooks - server - error in handle');
		console.log('=== Access to this protected route failed: ===');
		console.log(event.url.href);
		throw error(500, 'Error in handle: ' + err);
	}

	// try {
	// 	const sessionId = event.cookies.get('session_id');
	// 	console.log('🎣 hooks - server - sessionId')
	// 	console.log(sessionId);
	// 	if (sessionId) {
	// 		const session: Session = await redisCache.getSession(sessionId) as Session;
	// 		console.log('🎣 hooks - server - session');
	// 		console.log(session);
	// 		if (session && session?.loggedIn) {
	// 			event.locals.sessionData = session;
	// 			if (event.route.id?.includes('(admin)')) {
	// 				console.log('🎣 hooks - server - access to admin route');
	// 				// Add check if user is admin in backend here
	// 				// if (session.roles.includes('admin')) {

	// 				// } else {
	// 				// 	console.error('🎣 hooks - server - access attempt to admin route without admin role');
	// 				// 	redirectLogin(event.url.href);
	// 				// }
	// 			}

	// 		} else {
	// 			console.error('🔥 🎣 hooks - server - session expired in cache');
	// 			event.cookies.delete('session_id', {
	// 				path: '/',
	// 				expires: new Date(0)
	// 			});
	// 			redirectLogin(event.url.href);
	// 		}
	// 	} else {
	// 		console.error('🔥 🎣 hooks - server - access attempt to protected route without session_id in cookie');
	// 		redirectLogin(event.url.href);
	// 	};
	// }catch (err) {
	// 	console.error('🔥 🎣 hooks - server - error in handle');
	// 	console.log("=== Access to this protected route failed: ===");
	// 	console.log(event.url.href);
	// 	throw error (500, 'Error in handle');
	// }
	// }
	// return await resolve(event);
};

// 	// const sessionId = `session:${event.cookies.get('session_id')}`;
// 	console.log('🎣 hooks - server - event.url.href')
// 	console.log(event.url.href);
// 	// sessionId = `session:${sessionId}`;
// 	// console.log('🎣 hooks - server - sessionId');
// 	// console.log(sessionId);

// 	// Check for cookie in request:
// 	const sessionId = event.cookies.get('session_id');
// 	if (!sessionId) {
// 		// TBD add reset of sessionData: ???
// 		// event.locals.sessionData = null;
// 		const targetURL = event.request.url;
// 		if (event.route.id?.includes('(admin)')) {
// 			console.error('🎣 hooks - server - access attempt to admin route without session_id');
// 			redirect(307, '/');
// 		} else if (event.route.id?.includes('(protected)')) {
// 			console.error('🎣 hooks - server - access attempt to protected route without session_id');
// 			// console.log("===> hooks - server - !sessionId - redirecting to '/' <===");
// 			redirect(307, '/');
// 		}
// 	} else if (sessionId) {
// 		const session = await retrieveSession(sessionId);
// 		if (!session) {
// 			console.error('🎣 hooks - server - session expired in cache');
// 			event.cookies.delete('session_id', {
// 				path: '/',
// 				expires: new Date(0)
// 			});
// 			// console.log('🎣 hooks - server - locals after session expired');
// 			// console.log(event.locals);
// 			// console.log("===> hooks - server - session expired - redirecting to '/' <===");
// 			// redirects in case of a real login event, but misses the targetUrl.
// 			// if redirect to "/" here, then login is not successful in case of a real round-trip to identity service provider.
// 			redirect(307, '/login');
// 		} else {
// 			// console.log('🎣 hooks - server - sessionData - set');
// 			// Remove the handling via event.locals and use cache data instead!
// 			event.locals.sessionData = session;
// 		}
// 	}

// 	return await resolve(event);
// };

/* app.html before update:
<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8" />
		<link rel="icon" href="%sveltekit.assets%/favicon.png" />
		<link
			href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700,900&display=swap"
			rel="stylesheet"
		/>
		<meta name="viewport" content="width=device-width" />
		%sveltekit.head%
	</head>
	<body data-sveltekit-preload-data="hover">
		<div style="display: contents">%sveltekit.body%</div>
	</body>
</html>
*/
