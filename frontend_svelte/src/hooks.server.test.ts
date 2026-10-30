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
	test.each([
		{ accept: 'text/html', 'x-sveltekit-action': 'false' },
		{ accept: 'application/json', 'x-sveltekit-action': 'true' }
	])('redirects an unauthenticated form action to login as a GET request (%j)', async (headers) => {
		mocks.getSession.mockResolvedValue(undefined);
		const url = new URL('https://app.example/account/merge?/abandon');

		await expect(
			handle({
				event: {
					request: new Request(url, { method: 'POST', headers }),
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

	test('rejects an expired-session background request without redirecting it to login', async () => {
		mocks.getSession.mockResolvedValue(undefined);
		const url = new URL('https://app.example/api/v1/socketio-ticket');
		const resolve = vi.fn();

		await expect(
			handle({
				event: {
					request: new Request(url, { method: 'POST' }),
					url,
					route: { id: '/(plain)/(protected)/api/v1/socketio-ticket' },
					cookies: { get: () => 'expired-session' },
					locals: {}
				},
				resolve
			} as never)
		).rejects.toMatchObject({ status: 401 });
		expect(resolve).not.toHaveBeenCalled();
	});

	test('preserves login redirects for SvelteKit page-data navigation', async () => {
		mocks.getSession.mockResolvedValue(undefined);
		const url = new URL('https://app.example/question/setup?mode=edit');

		await expect(
			handle({
				event: {
					request: new Request(url),
					isDataRequest: true,
					url,
					route: { id: '/(layout)/(protected)/question/setup' },
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
