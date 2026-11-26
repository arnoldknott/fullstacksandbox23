import { beforeEach, describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	get: vi.fn(),
	getEntity: vi.fn(),
	getSnapshot: vi.fn(),
	getAccessPolicies: vi.fn()
}));

vi.mock('$lib/server/apis/backendApi', () => ({
	backendAPI: { ...mocks, getAllIdentities: vi.fn().mockResolvedValue([]) }
}));
vi.mock('$lib/server/apis/msgraph', () => ({
	microsoftGraph: { getAttachedTeamsAsIdentities: vi.fn().mockResolvedValue([]) }
}));

import { load } from './+page.server';

describe('text setup snapshot', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.getEntity.mockResolvedValue({
			entity: { id: 'text-1', content: 'parent' },
			cursor: 10
		});
		mocks.getSnapshot.mockImplementation((_sessionId: string, path: string) =>
			Promise.resolve(
				path.startsWith('/text/snapshot')
					? { entities: [{ id: 'child-text-1' }], cursor: 11 }
					: { entities: [{ id: 'number-1' }], cursor: 12 }
			)
		);
		mocks.getAccessPolicies.mockResolvedValue([
			{ resource_id: 'text-1', action: 'own' },
			{ resource_id: 'child-text-1', action: 'read' },
			{ resource_id: 'number-1', action: 'write' }
		]);
		mocks.get.mockResolvedValue(
			Response.json([
				{ parent_id: 'text-1', child_id: 'child-text-1', inherit: true, order: 1 },
				{ parent_id: 'text-1', child_id: 'number-1', inherit: false, order: 2 }
			])
		);
	});

	test('loads the text and linked child snapshots with access metadata', async () => {
		const result = await load({
			params: { id: 'text-1' },
			locals: { sessionData: { sessionId: 'session-1' } }
		} as never);
		if (!result) throw new Error('Text setup load returned no data.');

		expect(mocks.getEntity).toHaveBeenCalledWith('session-1', '/text/text-1');
		expect(mocks.getSnapshot).toHaveBeenCalledWith(
			'session-1',
			expect.stringContaining('parent-id=text-1')
		);
		expect(mocks.getAccessPolicies).toHaveBeenCalledWith('session-1', [
			'text-1',
			'child-text-1',
			'number-1'
		]);
		expect(result.payload.text).toMatchObject({
			id: 'text-1',
			access_policies: [{ resource_id: 'text-1', action: 'own' }]
		});
		expect(result.payload.texts[0]).toMatchObject({
			id: 'child-text-1',
			access_policies: [{ resource_id: 'child-text-1', action: 'read' }],
			hierarchies: [{ parent_id: 'text-1', child_id: 'child-text-1', inherit: true, order: 1 }]
		});
		expect(result.payload.numbers[0]).toMatchObject({
			id: 'number-1',
			access_policies: [{ resource_id: 'number-1', action: 'write' }]
		});
		expect(result.payload.textCursor).toBe(10);
		expect(result.payload.textsCursor).toBe(11);
		expect(result.payload.numbersCursor).toBe(12);
		expect(result.payload.identities.at(-1)).toMatchObject({ id: 'public' });
	});

	test('propagates hierarchy request failures', async () => {
		mocks.get.mockResolvedValue(new Response(null, { status: 403 }));
		await expect(
			load({
				params: { id: 'text-1' },
				locals: { sessionData: { sessionId: 'session-1' } }
			} as never)
		).rejects.toMatchObject({ status: 403 });
	});
});
