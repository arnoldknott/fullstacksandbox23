import { afterEach, describe, expect, test, vi } from 'vitest';

import { backendAPI } from './backendApi';

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
