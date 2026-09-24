import { v4 } from 'uuid';

import { IdentityProvider } from '$lib/identityProvider';
import { redisCache } from '$lib/server/cache';
import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth/microsoft';
import { SessionStatus } from '$lib/session';
// import { redirect } from '@sveltejs/kit';
import type { Session } from '$lib/types';

import type { PageServerLoad } from '../$types';

const appConfig = await AppConfig.getInstance();

// export const load: PageServerLoad = async ({ url, cookies, request }) => {
export const load: PageServerLoad = async ({ url, request }) => {
	let loginUrl: string;
	const sessionId = v4();
	try {
		// create the session uuid here:
		const userAgent = request.headers.get('user-agent');
		// TBD: check the typing of that one:
		const sessionData: Session = {
			status: SessionStatus.AUTHENTICATION_PENDING,
			loggedIn: false,
			identityProvider: IdentityProvider.MICROSOFT,
			userAgent: userAgent || '',
			sessionId: sessionId
		};

		await redisCache.setSession(
			sessionId,
			'$',
			JSON.stringify(sessionData),
			appConfig.authentication_timeout
		);

		// cookies.set('session_id', sessionId, {
		// 	path: '/',
		// 	...appConfig.authentication_cookie_options
		// });

		const targetUrl = url.searchParams.get('target-url') || undefined;
		const parentUrl = url.searchParams.get('parent-url') || undefined;

		// if (parentUrl) {
		// 	targetUrl = parentUrl;
		// }

		loginUrl = await msalAuthProvider.signIn(sessionId, url.origin, targetUrl, parentUrl);
		// console.log('=== login - server - loginUrl ===');
		// console.log(loginUrl);
	} catch (err) {
		console.error('🔥 🚪 login - server - sign in redirect failed');
		console.error(err);
		throw err; // TBD consider redirect to "/" instead here?
	}
	// redirect(302, loginUrl);
	return { loginUrl: loginUrl, sessionId: sessionId };
};
