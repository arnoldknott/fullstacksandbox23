import { redisCache } from '$lib/server/cache';
import { SessionStatus } from '$lib/session';

import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	const session = locals.sessionData;
	const showWelcome = Boolean(
		session?.loggedIn &&
		session.currentUser?.id &&
		session.status === SessionStatus.REGISTRATION_PENDING &&
		session.welcomePending === true
	);

	if (showWelcome) {
		// Consume only the one-time display flag. Registration remains pending
		// until the user submits the welcome form.
		await redisCache.setSession(session.sessionId, '$.welcomePending', JSON.stringify(false));
		session.welcomePending = false;
	}

	return { showWelcome };
};
