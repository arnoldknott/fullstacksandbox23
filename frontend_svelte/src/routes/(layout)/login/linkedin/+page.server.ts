import { v4 } from 'uuid';

import { IdentityProvider } from '$lib/identityProvider';
import { redisCache } from '$lib/server/cache';
import AppConfig from '$lib/server/config';
import { linkedinAuthProvider } from '$lib/server/oauth/linkedin';
import { SessionStatus } from '$lib/session';
import type { Session } from '$lib/types';

import type { PageServerLoad } from './$types';

const appConfig = await AppConfig.getInstance();

export const load: PageServerLoad = async ({ url, request }) => {
	const sessionId = v4();
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
	const loginUrl = await linkedinAuthProvider.signIn(
		sessionId,
		url.origin,
		url.searchParams.get('target-url') || undefined,
		url.searchParams.get('parent-url') || undefined
	);
	return { loginUrl, sessionId };
};
