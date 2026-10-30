import { describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	getSession: vi.fn(),
	setSession: vi.fn(),
	signIn: vi.fn()
}));
vi.mock('$lib/server/cache', () => ({
	redisCache: { getSession: mocks.getSession, setSession: mocks.setSession }
}));
vi.mock('$lib/server/config', () => ({
	default: { getInstance: () => Promise.resolve({ authentication_timeout: 600 }) }
}));
vi.mock('$lib/server/oauth/microsoft', () => ({
	msalAuthProvider: { signIn: mocks.signIn }
}));

import { load } from './+page.server';

describe('Microsoft presentation reauthentication', () => {
	test('keeps the existing session and complete slide target in the authorization transaction', async () => {
		const target =
			'https://app.example/presentation/teachingengagement/cbs-2026-11?presenter=true#/inspiration-books/1';
		mocks.getSession.mockResolvedValue({
			loggedIn: true,
			sessionId: 'session',
			sessionOwnerProvider: 'microsoft',
			currentUser: { id: 'presenter', azure_user_id: 'microsoft-presenter' }
		});
		mocks.signIn.mockResolvedValue('https://identity.example/authorize');

		const result = await load({
			url: new URL(`https://app.example/login/microsoft?target-url=${encodeURIComponent(target)}`),
			request: new Request('https://app.example/login/microsoft'),
			cookies: { get: () => 'session' }
		} as never);

		expect(result).toEqual({
			sessionId: 'session',
			loginUrl: 'https://identity.example/authorize'
		});
		expect(mocks.setSession).not.toHaveBeenCalled();
		expect(mocks.signIn).toHaveBeenCalledWith(
			'session',
			'https://app.example',
			target,
			undefined,
			'reauthentication',
			undefined
		);
	});
});
