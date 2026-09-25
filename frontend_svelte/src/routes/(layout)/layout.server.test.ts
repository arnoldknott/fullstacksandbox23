import { beforeEach, describe, expect, it, vi } from 'vitest';

import { redisCache } from '$lib/server/cache';
import { SessionStatus } from '$lib/session';

import { load } from './+layout.server';
import type { LayoutServerLoad } from './$types';

vi.mock('$lib/server/cache', () => ({ redisCache: { setSession: vi.fn() } }));

function event(status: SessionStatus, loggedIn = true, hasUser = true, welcomePending = true) {
	return {
		locals: {
			sessionData: {
				sessionId: 'test-session',
				loggedIn,
				status,
				welcomePending,
				currentUser: hasUser ? { id: 'internal-user' } : undefined
			}
		}
	} as Parameters<LayoutServerLoad>[0];
}

describe('first-login welcome', () => {
	beforeEach(() => vi.clearAllMocks());

	it('shows once while registration stays pending until profile save', async () => {
		const request = event(SessionStatus.REGISTRATION_PENDING);
		expect(await load(request)).toEqual({ showWelcome: true });
		expect(redisCache.setSession).toHaveBeenCalledWith(
			'test-session',
			'$.welcomePending',
			JSON.stringify(false)
		);
		expect(request.locals.sessionData.status).toBe(SessionStatus.REGISTRATION_PENDING);
		expect(await load(request)).toEqual({ showWelcome: false });
		expect(redisCache.setSession).toHaveBeenCalledTimes(1);
	});

	it.each([SessionStatus.REGISTERED, SessionStatus.AUTHENTICATION_PENDING])(
		'does not show for %s sessions',
		async (status) => {
			expect(await load(event(status))).toEqual({ showWelcome: false });
			expect(redisCache.setSession).not.toHaveBeenCalled();
		}
	);

	it('does not reopen for a pending registration after the display flag was consumed', async () => {
		expect(await load(event(SessionStatus.REGISTRATION_PENDING, true, true, false))).toEqual({
			showWelcome: false
		});
		expect(redisCache.setSession).not.toHaveBeenCalled();
	});

	it('does not show for anonymous sessions or failed backend signup', async () => {
		expect(await load(event(SessionStatus.REGISTRATION_PENDING, false))).toEqual({
			showWelcome: false
		});
		expect(await load(event(SessionStatus.REGISTRATION_PENDING, true, false))).toEqual({
			showWelcome: false
		});
		expect(redisCache.setSession).not.toHaveBeenCalled();
	});
});
