/** @type {import('@sveltejs/kit').Handle} */
import { getSession, updateSessionExpiry } from '$lib/server/cache';
import type { Session } from '$lib/types'; // TBD: move to app.d.ts (look at new template from ground up installation)
import { redirect } from '@sveltejs/kit';

const retrieveSession = async (sessionId: string | null): Promise<Session | void> => {
	if (sessionId) {
		const session = await getSession(sessionId);
		if (session) {
			await updateSessionExpiry(sessionId);
			return session;
		} else {
			console.error('🎣 hooks - server - getSession failed');
		}
	}
};

export const handle = async ({ event, resolve }) => {
	const sessionId = event.cookies.get('session_id');

	if (!sessionId) {
		if (event.route.id?.includes('(admin)')) {
			console.error('🎣 hooks - server - access attempt to admin route without session_id');
			redirect(307, '/');
		} else if (event.route.id?.includes('(protected)')) {
			console.error('🎣 hooks - server - access attempt to protected route without session_id');
			redirect(307, '/');
		}
	} else if (sessionId) {
		const session = await retrieveSession(sessionId);
		if (!session) {
			console.error('🎣 hooks - server - session expired');
			event.cookies.delete('session_id', {
				path: '/',
				expires: new Date(0)
			});
			console.log('🎣 hooks - server - locals after session expired');
			console.log(event.locals);
			redirect(307, '/');
		} else {
			event.locals.sessionData = session;
		}
	}

	return await resolve(event);
};

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
