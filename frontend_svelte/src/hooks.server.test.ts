import { describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	getSession: vi.fn(),
	renewSessionIfNeeded: vi.fn()
}));

vi.mock('$lib/server/apis/backendApi', () => ({
	backendAPI: { get: vi.fn() }
}));
vi.mock('$lib/server/cache', () => ({
	redisCache: {
		getSession: mocks.getSession,
		renewSessionIfNeeded: mocks.renewSessionIfNeeded
	}
}));
vi.mock('$lib/server/config', () => ({
	default: {
		getInstance: () => Promise.resolve({ session_cookie_options: {} })
	}
}));

import { handle } from './hooks.server';

describe('protected-route authentication redirects', () => {
	test('redirects an unauthenticated form action to login as a GET request', async () => {
		mocks.getSession.mockResolvedValue(undefined);
		const url = new URL('https://app.example/account/merge?/abandon');

		await expect(
			handle({
				event: {
					request: new Request(url, { method: 'POST' }),
					url,
					route: { id: '/(layout)/(protected)/account/merge' },
					cookies: { get: () => 'expired-session' },
					locals: {}
				},
				resolve: vi.fn()
			} as never)
		).rejects.toMatchObject({
			status: 303,
			location: `/login?target-url=${encodeURIComponent(url.href)}`
		});
	});
});
