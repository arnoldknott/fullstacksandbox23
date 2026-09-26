import { afterEach, describe, expect, test, vi } from 'vitest';

import { IdentityProvider } from '$lib/identityProvider';
import { redisCache } from '$lib/server/cache';
import {
	linkedinAuthProvider,
	LinkedInReauthenticationRequiredError
} from '$lib/server/oauth/linkedin';
import { msalAuthProvider } from '$lib/server/oauth/microsoft';

import { backendAPI, backendAuthProvider } from './backendApi';

describe('BackendAPI.getSnapshot', () => {
	afterEach(() => vi.restoreAllMocks());

	test('returns parsed entities and cursor for a public snapshot', async () => {
		const get = vi.spyOn(backendAPI, 'get').mockResolvedValue(
			new Response(JSON.stringify([{ id: 'entity-1' }]), {
				status: 200,
				headers: { 'X-Entity-Cursor': '42' }
			})
		);

		await expect(
			backendAPI.getSnapshot<{ id: string }>(null, '/quiz/message/snapshot')
		).resolves.toEqual({ entities: [{ id: 'entity-1' }], cursor: 42 });
		expect(get).toHaveBeenCalledWith(null, '/quiz/message/snapshot');
	});

	test.each([
		new Response(null, { status: 401 }),
		new Response('[]', { status: 200 }),
		new Response('[]', { status: 200, headers: { 'X-Entity-Cursor': 'invalid' } })
	])('rejects an invalid snapshot response', async (response) => {
		vi.spyOn(backendAPI, 'get').mockResolvedValue(response);

		await expect(backendAPI.getSnapshot(null, '/snapshot')).rejects.toBeDefined();
	});
});

describe('BackendAuthenticationProvider', () => {
	afterEach(() => vi.restoreAllMocks());

	test('uses the Microsoft backend access token and requested scopes', async () => {
		vi.spyOn(redisCache, 'getSession').mockResolvedValue(IdentityProvider.MICROSOFT);
		const microsoft = vi.spyOn(msalAuthProvider, 'getAccessToken').mockResolvedValue('azure-token');
		const linkedin = vi.spyOn(linkedinAuthProvider, 'getIdentityToken');

		await expect(
			backendAuthProvider.getAccessToken('session', ['api://backend/api.read'])
		).resolves.toBe('azure-token');
		expect(microsoft).toHaveBeenCalledWith('session', ['api://backend/api.read']);
		expect(linkedin).not.toHaveBeenCalled();
	});

	test('uses the LinkedIn identity token without Microsoft scopes', async () => {
		vi.spyOn(redisCache, 'getSession').mockResolvedValue(IdentityProvider.LINKEDIN);
		const microsoft = vi.spyOn(msalAuthProvider, 'getAccessToken');
		const linkedin = vi
			.spyOn(linkedinAuthProvider, 'getIdentityToken')
			.mockResolvedValue('linkedin-id-token');

		await expect(
			backendAuthProvider.getAccessToken('session', ['api://backend/api.read'])
		).resolves.toBe('linkedin-id-token');
		expect(linkedin).toHaveBeenCalledWith('session');
		expect(microsoft).not.toHaveBeenCalled();
	});

	test('redirects expired LinkedIn authentication to provider login', async () => {
		vi.spyOn(redisCache, 'getSession').mockResolvedValue(IdentityProvider.LINKEDIN);
		vi.spyOn(linkedinAuthProvider, 'getIdentityToken').mockRejectedValue(
			new LinkedInReauthenticationRequiredError('expired')
		);

		await expect(backendAuthProvider.getAccessToken('session')).rejects.toMatchObject({
			status: 307,
			location: '/login/linkedin?target-url=%2F'
		});
	});

	test('rejects a session without a supported active provider', async () => {
		vi.spyOn(redisCache, 'getSession').mockResolvedValue(undefined);

		await expect(backendAuthProvider.getAccessToken('session')).rejects.toThrow(
			'no supported active identity provider'
		);
	});
});
