import { describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	getAccessToken: vi.fn(),
	renewSessionIfNeeded: vi.fn()
}));

vi.mock('$lib/server/apis/backendApi', () => ({
	backendAuthProvider: { getAccessToken: mocks.getAccessToken }
}));
vi.mock('$lib/server/cache', () => ({
	redisCache: { renewSessionIfNeeded: mocks.renewSessionIfNeeded }
}));
vi.mock('$lib/server/config', () => ({
	default: {
		getInstance: () =>
			Promise.resolve({
				api_scope: 'api',
				session_cookie_options: { httpOnly: true, maxAge: 3600 }
			})
	}
}));

import { POST } from './+server';

describe('POST /session/touch', () => {
	test('renews the same session and synchronizes its cookie', async () => {
		mocks.getAccessToken.mockResolvedValue('token');
		mocks.renewSessionIfNeeded.mockResolvedValue('renewed');
		const cookies = { set: vi.fn() };

		const response = await POST({
			locals: { sessionData: { loggedIn: true, sessionId: 'session-1' } },
			cookies
		} as never);

		expect(response.status).toBe(204);
		expect(mocks.renewSessionIfNeeded).toHaveBeenCalledWith('session-1');
		expect(cookies.set).toHaveBeenCalledWith('session_id', 'session-1', {
			path: '/',
			httpOnly: true,
			maxAge: 3600
		});
	});

	test('does not revive a missing session or set a cookie', async () => {
		mocks.getAccessToken.mockResolvedValue('token');
		mocks.renewSessionIfNeeded.mockResolvedValue('missing');
		const cookies = { set: vi.fn() };

		const response = await POST({
			locals: { sessionData: { loggedIn: true, sessionId: 'session-1' } },
			cookies
		} as never);

		expect(response.status).toBe(401);
		expect(cookies.set).not.toHaveBeenCalled();
	});
});
