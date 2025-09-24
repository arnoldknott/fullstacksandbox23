import { v4 } from 'uuid';
import { msalAuthProvider } from '$lib/server/oauth';
import { redisCache } from '$lib/server/cache';
import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import type { Session } from '$lib/types';
import { SessionStatus } from '$lib/server/oauth';
import AppConfig from '$lib/server/config';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ url, cookies, request }) => {
	let loginUrl: string;
	try {
		// create the session uuid here:
		const sessionId = v4();
		const userAgent = request.headers.get('user-agent');
		// TBD: check the typing of that one:
		const sessionData: Session = {
			status: SessionStatus.AUTHENTICATION_PENDING,
			loggedIn: false,
			userAgent: userAgent || '',
			sessionId: sessionId
		};

		await redisCache.setSession(
			sessionId,
			'$',
			JSON.stringify(sessionData),
			appConfig.authentication_timeout
		);

		cookies.set('session_id', sessionId, {
			path: '/',
			...appConfig.authentication_cookie_options
		});

		const targetURL = url.searchParams.get('targetURL') || undefined;

		loginUrl = await msalAuthProvider.signIn(sessionId, url.origin, targetURL);
	} catch (err) {
		console.error('🔥 🚪 login - server - sign in redirect failed');
		console.error(err);
		throw err; // TBD consider redirect to "/" instead here?
	}
	redirect(302, loginUrl);
};
