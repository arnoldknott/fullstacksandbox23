import { afterEach, describe, expect, test, vi } from 'vitest';

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

	test('uses the frontend application credential independently of user scopes', async () => {
		const application = vi
			.spyOn(msalAuthProvider, 'getApplicationAccessToken')
			.mockResolvedValue('frontend-service-token');

		await expect(
			backendAuthProvider.getAccessToken('session', ['api://backend/api.read'])
		).resolves.toBe('frontend-service-token');
		expect(application).toHaveBeenCalledOnce();
	});

	test('sends the service token and opaque session reference', async () => {
		vi.spyOn(msalAuthProvider, 'getApplicationAccessToken').mockResolvedValue(
			'frontend-service-token'
		);
		const fetchMock = vi
			.spyOn(globalThis, 'fetch')
			.mockResolvedValue(new Response('{}', { status: 200 }));

		await backendAPI.get('session-reference', '/user/me');

		const request = fetchMock.mock.calls[0]?.[0];
		expect(request).toBeInstanceOf(Request);
		expect((request as Request).headers.get('Authorization')).toBe('Bearer frontend-service-token');
		expect((request as Request).headers.get('X-Application-Session')).toBe('session-reference');
	});
});
