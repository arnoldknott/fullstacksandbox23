import { v4 } from 'uuid';

import { IdentityProvider } from '$lib/identityProvider';
import { redisCache } from '$lib/server/cache';
import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth/microsoft';
import { SessionStatus } from '$lib/session';
import type { Session } from '$lib/types';

import type { PageServerLoad } from '../$types';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ url, request, cookies }) => {
	let loginUrl: string;
	const existingSessionId = cookies.get('session_id');
	const existingSession = existingSessionId
		? await redisCache.getSession<Session>(existingSessionId)
		: undefined;
	const sessionId = existingSession?.loggedIn ? existingSessionId! : v4();
	try {
		// Create a pending session only for an initial unauthenticated login.
		if (!existingSession?.loggedIn) {
			const sessionData: Session = {
				status: SessionStatus.AUTHENTICATION_PENDING,
				loggedIn: false,
				identityProvider: IdentityProvider.MICROSOFT,
				userAgent: request.headers.get('user-agent') || '',
				sessionId
			};
			await redisCache.setSession(
				sessionId,
				'$',
				JSON.stringify(sessionData),
				appConfig.authentication_timeout
			);
		}

		const targetUrl = url.searchParams.get('target-url') || undefined;
		const parentUrl = url.searchParams.get('parent-url') || undefined;
		loginUrl = await msalAuthProvider.signIn(
			sessionId,
			url.origin,
			targetUrl,
			parentUrl,
			existingSession?.loggedIn ? 'reauthentication' : 'login'
		);
	} catch (err) {
		console.error('🔥 🚪 login - server - sign in redirect failed');
		console.error(err);
		throw err;
	}
	return { loginUrl, sessionId };
};
