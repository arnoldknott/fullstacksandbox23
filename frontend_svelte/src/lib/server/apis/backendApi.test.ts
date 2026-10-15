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

describe('entity handoff and scoped policies', () => {
	afterEach(() => vi.restoreAllMocks());
	test('loads a single entity without changing its response body', async () => {
		const get = vi
			.spyOn(backendAPI, 'get')
			.mockResolvedValue(Response.json({ id: 'one' }, { headers: { 'X-Entity-Cursor': '0' } }));
		await expect(backendAPI.getEntity('session', '/presentation/one')).resolves.toEqual({
			entity: { id: 'one' },
			cursor: 0
		});
		expect(get).toHaveBeenCalledWith('session', '/presentation/one');
	});
	test.each([null, '', ' ', '-1', '1.5', '42junk', '9007199254740992'])(
		'rejects invalid cursors on both read helpers: %s',
		async (cursor) => {
			vi.spyOn(backendAPI, 'get').mockImplementation(async () =>
				Response.json({}, { headers: cursor === null ? {} : { 'X-Entity-Cursor': cursor } })
			);
			await expect(backendAPI.getEntity(null, '/entity')).rejects.toMatchObject({ status: 502 });
			await expect(backendAPI.getSnapshot(null, '/snapshot')).rejects.toMatchObject({
				status: 502
			});
		}
	);
	test.each([403, 404])('preserves entity read failures: %s', async (status) => {
		vi.spyOn(backendAPI, 'get').mockResolvedValue(new Response(null, { status }));
		await expect(backendAPI.getEntity('session', '/entity')).rejects.toMatchObject({ status });
	});
	test('requests policies for unique resource identifiers and skips empty collections', async () => {
		const post = vi
			.spyOn(backendAPI, 'post')
			.mockResolvedValue(Response.json([{ resource_id: 'one' }]));
		await expect(backendAPI.getAccessPolicies('session', [])).resolves.toEqual([]);
		expect(post).not.toHaveBeenCalled();
		await expect(backendAPI.getAccessPolicies('session', ['one', 'one', 'two'])).resolves.toEqual([
			{ resource_id: 'one' }
		]);
		expect(post).toHaveBeenCalledExactlyOnceWith(
			'session',
			'/access/policy/resources',
			JSON.stringify(['one', 'two'])
		);
	});
	test('propagates policy read failures', async () => {
		vi.spyOn(backendAPI, 'post').mockResolvedValue(new Response(null, { status: 403 }));
		await expect(backendAPI.getAccessPolicies('session', ['one'])).rejects.toMatchObject({
			status: 403
		});
	});
});
