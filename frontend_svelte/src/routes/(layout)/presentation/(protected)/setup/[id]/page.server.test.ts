import { beforeEach, describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({ get: vi.fn(), getSnapshot: vi.fn() }));

vi.mock('$lib/server/apis/backendApi', () => ({
	backendAPI: { ...mocks, getAllIdentities: vi.fn().mockResolvedValue([]) }
}));
vi.mock('$lib/server/apis/msgraph', () => ({
	microsoftGraph: { getAttachedTeamsAsIdentities: vi.fn().mockResolvedValue([]) }
}));

import { load } from './+page.server';

const policy = { resource_id: 'presentation-1', identity_id: 'group-1', action: 'write' };
const event = {
	params: { id: 'presentation-1' },
	locals: { sessionData: { sessionId: 'session-1' } }
};

describe('presentation setup access snapshot', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.getSnapshot.mockImplementation((_sessionId: string, path: string) =>
			Promise.resolve(
				path.startsWith('/presentation/snapshot')
					? { entities: [{ id: 'presentation-1', access_right: 'own' }], cursor: 21 }
					: { entities: [{ id: 'question-1' }], cursor: 42 }
			)
		);
		mocks.get.mockImplementation((_sessionId: string, path: string) =>
			Promise.resolve(
				Response.json(
					path.endsWith('/Presentation')
						? [policy, { ...policy, resource_id: 'presentation-2' }]
						: []
				)
			)
		);
	});

	test('seeds only the selected presentation policies and keeps namespace cursors separate', async () => {
		const result = await load(event as never);
		if (!result) throw new Error('Presentation setup load returned no data.');
		expect(result.payload.presentation).toMatchObject({
			id: 'presentation-1',
			access_right: 'own',
			access_policies: [policy]
		});
		expect(result.payload.presentationCursor).toBe(21);
		expect(result.payload.cursor).toBe(42);
		expect(result.payload.questions[0].access_policies).toEqual([]);
	});

	test('fails instead of showing no shares when presentation policies cannot be loaded', async () => {
		mocks.get.mockResolvedValue(new Response(null, { status: 403 }));
		await expect(load(event as never)).rejects.toMatchObject({ status: 403 });
	});

	test('returns not found when the presentation is absent from the authorized snapshot', async () => {
		mocks.getSnapshot.mockResolvedValue({ entities: [], cursor: 21 });
		await expect(load(event as never)).rejects.toMatchObject({ status: 404 });
	});
});
