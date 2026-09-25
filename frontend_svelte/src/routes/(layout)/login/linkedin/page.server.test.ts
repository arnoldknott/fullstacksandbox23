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
vi.mock('$lib/server/oauth/linkedin', () => ({
	linkedinAuthProvider: { signIn: mocks.signIn }
}));
vi.mock('uuid', () => ({ v4: () => 'new-session' }));

import { load } from './+page.server';

describe('LinkedIn login route', () => {
	test('reauthenticates in the established session without replacing its data', async () => {
		mocks.getSession.mockResolvedValue({
			sessionId: 'existing-session',
			loggedIn: true,
			status: 'registered'
		});
		mocks.signIn.mockResolvedValue('https://linkedin.example/authorize');

		const result = await load({
			url: new URL('https://app.example/login/linkedin?target-url=%2Fquestion%2Fsetup'),
			request: new Request('https://app.example/login/linkedin'),
			cookies: { get: () => 'existing-session' }
		} as never);

		expect(result).toEqual({
			loginUrl: 'https://linkedin.example/authorize',
			sessionId: 'existing-session'
		});
		expect(mocks.setSession).not.toHaveBeenCalled();
		expect(mocks.signIn).toHaveBeenCalledWith(
			'existing-session',
			'https://app.example',
			'/question/setup',
			undefined,
			'reauthentication',
			undefined
		);
	});

	test('binds a link transaction to the established user and provider', async () => {
		mocks.getSession.mockResolvedValue({
			sessionId: 'existing-session',
			loggedIn: true,
			identityProvider: 'microsoft',
			currentUser: { id: 'internal-user-id' }
		});
		mocks.signIn.mockResolvedValue('https://linkedin.example/authorize');

		await load({
			url: new URL(
				'https://app.example/login/linkedin?intent=link&target-url=%2Fpresentation%2Fsetup'
			),
			request: new Request('https://app.example/login/linkedin'),
			cookies: { get: () => 'existing-session' }
		} as never);

		expect(mocks.setSession).not.toHaveBeenCalled();
		expect(mocks.signIn).toHaveBeenCalledWith(
			'existing-session',
			'https://app.example',
			'/presentation/setup',
			undefined,
			'link',
			{
				initiatingProvider: 'microsoft',
				initiatingUserId: 'internal-user-id'
			}
		);
	});
});
