import { v4 } from 'uuid';

import { IdentityProvider } from '$lib/identityProvider';
import { redisCache } from '$lib/server/cache';
import AppConfig from '$lib/server/config';
import { linkedinAuthProvider } from '$lib/server/oauth/linkedin';
import { SessionStatus } from '$lib/session';
import type { Session } from '$lib/types';

import type { PageServerLoad } from './$types';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ url, request, cookies }) => {
	const existingSessionId = cookies.get('session_id');
	const existingSession = existingSessionId
		? await redisCache.getSession<Session>(existingSessionId)
		: undefined;
	const sessionId = existingSession?.loggedIn ? existingSessionId! : v4();
	const linkRequested = url.searchParams.get('intent') === 'link';
	if (linkRequested && (!existingSession?.loggedIn || !existingSession.currentUser?.id)) {
		throw new Error('Account linking requires an established session.');
	}
	if (linkRequested && existingSession?.identityProvider === IdentityProvider.LINKEDIN) {
		throw new Error('Choose a different identity provider to link.');
	}
	if (!existingSession?.loggedIn) {
		const sessionData: Session = {
			status: SessionStatus.AUTHENTICATION_PENDING,
			loggedIn: false,
			identityProvider: IdentityProvider.LINKEDIN,
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
	const loginUrl = await linkedinAuthProvider.signIn(
		sessionId,
		url.origin,
		url.searchParams.get('target-url') || undefined,
		url.searchParams.get('parent-url') || undefined,
		linkRequested ? 'link' : existingSession?.loggedIn ? 'reauthentication' : 'login',
		linkRequested
			? {
					initiatingProvider: existingSession!.identityProvider!,
					initiatingUserId: existingSession!.currentUser!.id
				}
			: undefined
	);
	return { loginUrl, sessionId };
};
