import { beforeEach, describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({ graphGet: vi.fn(), getUserInfo: vi.fn() }));

vi.mock('$lib/server/config', () => ({
	default: { getInstance: () => Promise.resolve({ backend_fqdn: 'backend.example' }) }
}));
vi.mock('$lib/server/apis/msgraph', () => ({ microsoftGraph: { get: mocks.graphGet } }));
vi.mock('$lib/server/apis/linkedin', () => ({ linkedInAPI: { getUserInfo: mocks.getUserInfo } }));
vi.mock('$lib/server/oauth/linkedin', () => ({
	LinkedInReauthenticationRequiredError: class extends Error {}
}));

import { load } from './+layout.server';

describe('root layout provider-profile loading', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test.each([
		['microsoft', '/login/microsoft'],
		['microsoft', '/oauth/callback'],
		['linkedin', '/login/linkedin'],
		['linkedin', '/oauth/callback/linkedin']
	])('does not renew %s credentials during %s', async (provider, path) => {
		const result = await load({
			untrack: <T>(fn: () => T) => fn(),
			url: new URL(path, 'https://app.example'),
			locals: {
				sessionData: { loggedIn: true, sessionId: 'session', sessionOwnerProvider: provider }
			}
		} as never);

		expect(mocks.graphGet).not.toHaveBeenCalled();
		expect(mocks.getUserInfo).not.toHaveBeenCalled();
		expect(result).toMatchObject({ session: { loggedIn: true, sessionId: 'session' } });
	});

	test('still loads the Microsoft profile on the presentation route', async () => {
		mocks.graphGet.mockResolvedValue(Response.json({ displayName: 'Presenter' }));
		const result = await load({
			untrack: <T>(fn: () => T) => fn(),
			url: new URL('https://app.example/presentation/cbs?presenter=true'),
			locals: {
				sessionData: { loggedIn: true, sessionId: 'session', sessionOwnerProvider: 'microsoft' }
			}
		} as never);

		expect(mocks.graphGet).toHaveBeenCalledWith('session', '/me');
		expect(result).toMatchObject({ session: { microsoftProfile: { displayName: 'Presenter' } } });
	});
});
