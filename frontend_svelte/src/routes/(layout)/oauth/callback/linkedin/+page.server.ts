import { redirect } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';
import { redisCache } from '$lib/server/cache';
import AppConfig from '$lib/server/config';
import { linkedinAuthProvider } from '$lib/server/oauth/linkedin';
import { SessionStatus } from '$lib/session';

import type { PageServerLoad } from './$types';

const appConfig = await AppConfig.getInstance();

function safeTarget(target: string, origin: string): string {
	const targetUrl = new URL(target, origin);
	return targetUrl.origin === origin
		? `${targetUrl.pathname}${targetUrl.search}${targetUrl.hash}`
		: '/';
}

export const load: PageServerLoad = async ({ url, cookies }) => {
	const result = await linkedinAuthProvider.authenticateWithCode(url);
	const { sessionId } = result;

	const responseMe = await backendAPI.get(sessionId, '/user/me');
	if (responseMe.status !== 200 && responseMe.status !== 201) {
		throw new Error(`Backend LinkedIn signup failed with status ${responseMe.status}.`);
	}
	// This remains mutable so the commented development override below can be enabled directly.
	// eslint-disable-next-line prefer-const
	let sessionStatus =
		responseMe.status === 201 ? SessionStatus.REGISTRATION_PENDING : SessionStatus.REGISTERED;
	// TBD: To develop the first-login registration flow with an existing user,
	// assign REGISTRATION_PENDING here. Change it back when finished:
	// sessionStatus = SessionStatus.REGISTRATION_PENDING;
	await redisCache.setSession(sessionId, '$.status', JSON.stringify(sessionStatus));
	await redisCache.setSession(
		sessionId,
		'$.welcomePending',
		JSON.stringify(sessionStatus === SessionStatus.REGISTRATION_PENDING)
	);
	const currentUser = await responseMe.json();
	await redisCache.setSession(sessionId, '$.currentUser', JSON.stringify(currentUser));
	await redisCache.setSession(sessionId, '$.sessionId', JSON.stringify(sessionId));
	await redisCache.setSession(sessionId, '$.loggedIn', JSON.stringify(true));
	const cookieOptions = appConfig.session_cookie_options as Record<string, unknown>;
	cookies.set('session_id', sessionId, {
		path: '/',
		...cookieOptions
	});

	if (result.parentUrl) return { parentUrl: result.parentUrl };
	redirect(302, safeTarget(result.targetUrl, url.origin));
};
