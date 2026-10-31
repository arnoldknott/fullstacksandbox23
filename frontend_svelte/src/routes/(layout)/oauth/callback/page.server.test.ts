import { describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	decodeState: vi.fn(),
	authenticateWithCode: vi.fn(),
	getAccessToken: vi.fn(),
	get: vi.fn(),
	setSession: vi.fn(),
	updateSessionExpiry: vi.fn()
}));

vi.mock('$lib/server/config', () => ({
	default: {
		getInstance: () =>
			Promise.resolve({
				session_cookie_options: {}
			})
	}
}));
vi.mock('$lib/server/cache', () => ({
	redisCache: { setSession: mocks.setSession, updateSessionExpiry: mocks.updateSessionExpiry }
}));
vi.mock('$lib/server/apis/backendApi', () => ({ backendAPI: { get: mocks.get } }));
vi.mock('$lib/server/oauth/accountLink', () => ({ completeAccountLink: vi.fn() }));

vi.mock('$lib/server/oauth/microsoft', async () => {
	const { OAuthTransactionUnavailableError } = await import('$lib/server/oauth/base');
	return {
		msalAuthProvider: {
			authenticateWithCode: mocks.authenticateWithCode,
			getAccessToken: mocks.getAccessToken,
			decodeState: mocks.decodeState.mockRejectedValue(
				new OAuthTransactionUnavailableError('Microsoft authorization session was not found.')
			)
		}
	};
});

import { load } from './+page.server';

describe('Microsoft callback route', () => {
	test.each([
		[
			'https://app.example/presentation/teachingengagement/cbs-2026-11?presenter=true#/inspiration-books/2',
			'/presentation/teachingengagement/cbs-2026-11?presenter=true#/inspiration-books/2'
		],
		['https://other.example/target', '/']
	])(
		'returns safely to the stored destination after reauthentication (%s)',
		async (target, expected) => {
			mocks.decodeState.mockResolvedValueOnce({
				sessionId: 'session',
				targetUrl: target,
				intent: 'reauthentication'
			});
			mocks.get.mockResolvedValueOnce(Response.json({ id: 'presenter' }));
			const cookies = { set: vi.fn() };

			await expect(
				load({
					url: new URL('https://app.example/oauth/callback?code=fresh&state=state'),
					cookies
				} as never)
			).rejects.toMatchObject({ status: 302, location: expected });
			expect(cookies.set).toHaveBeenCalledWith('session_id', 'session', { path: '/' });
		}
	);

	test('redirects a stale callback instead of returning an internal error', async () => {
		await expect(
			load({
				url: new URL('https://app.example/oauth/callback?code=used&state=expired'),
				cookies: {}
			} as never)
		).rejects.toMatchObject({ status: 302, location: '/' });
	});

	test('restarts an expired transaction and preserves its destination', async () => {
		const { OAuthTransactionUnavailableError } = await import('$lib/server/oauth/base');
		mocks.decodeState.mockRejectedValueOnce(
			new OAuthTransactionUnavailableError('OAuth transaction expired.', {
				intent: 'link',
				targetUrl: '/presentation/setup?mode=edit',
				parentUrl: 'https://parent.example/presentation'
			})
		);

		await expect(
			load({
				url: new URL('https://app.example/oauth/callback?code=expired&state=expired'),
				cookies: {}
			} as never)
		).rejects.toMatchObject({
			status: 302,
			location:
				'/login/microsoft?target-url=%2Fpresentation%2Fsetup%3Fmode%3Dedit&parent-url=https%3A%2F%2Fparent.example%2Fpresentation&intent=link'
		});
	});
});
