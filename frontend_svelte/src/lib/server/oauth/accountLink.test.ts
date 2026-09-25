import { beforeEach, describe, expect, test, vi } from 'vitest';

import { IdentityProvider } from '$lib/identityProvider';

const mocks = vi.hoisted(() => ({
	getSession: vi.fn(),
	setSession: vi.fn(),
	post: vi.fn(),
	get: vi.fn(),
	getMicrosoftToken: vi.fn(),
	getLinkedInToken: vi.fn()
}));

vi.mock('../config', () => ({
	default: { getInstance: () => Promise.resolve({ authentication_timeout: 600 }) }
}));
vi.mock('../cache', () => ({
	redisCache: { getSession: mocks.getSession, setSession: mocks.setSession }
}));
vi.mock('../apis/backendApi', () => ({
	backendAPI: { post: mocks.post, get: mocks.get }
}));
vi.mock('./microsoft', () => ({
	msalAuthProvider: { getAccessToken: mocks.getMicrosoftToken }
}));
vi.mock('./linkedin', () => ({
	linkedinAuthProvider: { getIdentityToken: mocks.getLinkedInToken }
}));

import { completeAccountLink } from './accountLink';

describe('completeAccountLink', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.getSession.mockResolvedValue({
			loggedIn: true,
			identityProvider: IdentityProvider.LINKEDIN,
			currentUser: { id: 'surviving-user' }
		});
		mocks.getMicrosoftToken.mockResolvedValue('microsoft-proof');
	});

	test('stores a short-lived preview when the linked identity already has a user', async () => {
		mocks.post.mockResolvedValue(
			new Response(
				JSON.stringify({
					result: 'merge-required',
					preview_hash: 'preview-hash',
					settings: { contrast: { survivor: 0, source: 0.5 } },
					defaults: { contrast: 'source' }
				}),
				{ status: 200 }
			)
		);

		const result = await completeAccountLink(
			'session-id',
			{
				targetUrl: '/presentation/setup',
				initiatingProvider: IdentityProvider.LINKEDIN,
				initiatingUserId: 'surviving-user'
			},
			IdentityProvider.MICROSOFT
		);

		expect(result).toBe('merge-required');
		expect(mocks.post).toHaveBeenCalledWith(
			'session-id',
			'/user/me/link/preview',
			'{}',
			undefined,
			{},
			{ 'X-Account-Link-Authorization': 'Bearer microsoft-proof' }
		);
		const stored = JSON.parse(mocks.setSession.mock.calls[0][2]);
		expect(stored).toMatchObject({
			result: 'merge-required',
			preview_hash: 'preview-hash',
			linkedProvider: IdentityProvider.MICROSOFT,
			targetUrl: '/presentation/setup'
		});
		expect(stored.expiresAt).toBeGreaterThan(Date.now());
	});

	test('reloads the current user after direct attachment', async () => {
		mocks.post.mockResolvedValue(
			new Response(JSON.stringify({ result: 'linked' }), { status: 200 })
		);
		mocks.get.mockResolvedValue(
			new Response(JSON.stringify({ id: 'surviving-user', azure_user_id: 'azure-id' }), {
				status: 200
			})
		);

		const result = await completeAccountLink(
			'session-id',
			{
				targetUrl: '/dashboard',
				initiatingProvider: IdentityProvider.LINKEDIN,
				initiatingUserId: 'surviving-user'
			},
			IdentityProvider.MICROSOFT
		);

		expect(result).toBe('linked');
		expect(mocks.setSession).toHaveBeenCalledWith(
			'session-id',
			'$.currentUser',
			JSON.stringify({ id: 'surviving-user', azure_user_id: 'azure-id' })
		);
	});

	test('rejects a callback that is not bound to the current session user', async () => {
		await expect(
			completeAccountLink(
				'session-id',
				{
					targetUrl: '/dashboard',
					initiatingProvider: IdentityProvider.LINKEDIN,
					initiatingUserId: 'different-user'
				},
				IdentityProvider.MICROSOFT
			)
		).rejects.toThrow('no longer matches');
		expect(mocks.getMicrosoftToken).not.toHaveBeenCalled();
		expect(mocks.post).not.toHaveBeenCalled();
	});
});
