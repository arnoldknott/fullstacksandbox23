import { beforeEach, expect, test, vi } from 'vitest';
const mocks = vi.hoisted(() => ({ get: vi.fn(), getEntity: vi.fn(), getSnapshot: vi.fn() }));
vi.mock('$lib/server/apis/backendApi', () => ({ backendAPI: mocks }));
vi.mock('$lib/server/apis/integrations', () => ({
	MicrosoftAccountLinking: { getUsers: vi.fn() }
}));
import { load } from './+page.server';
const event = {
	params: { ueberGroupId: 'selected' },
	locals: { sessionData: { sessionId: 'session' } },
	parent: async () => ({ session: { currentUser: { azure_token_roles: [] } } })
};
beforeEach(() => {
	vi.resetAllMocks();
	mocks.getEntity.mockResolvedValue({ entity: { id: 'selected' }, cursor: 10 });
	mocks.getSnapshot.mockResolvedValue({
		entities: [{ id: 'linked' }, { id: 'available' }],
		cursor: 12
	});
	mocks.get.mockImplementation(async (_session: string, path: string) => {
		if (path.includes('/right/')) return Response.json('own');
		if (path.endsWith('/created')) return Response.json('2026-01-01T00:00:00Z');
		return Response.json([{ parent_id: 'selected', child_id: 'linked' }]);
	});
});
test('loads one ueber group while retaining groups available for linking', async () => {
	const result = await load(event as never);
	expect(mocks.getEntity).toHaveBeenCalledWith('session', '/uebergroup/selected');
	expect(mocks.getSnapshot).toHaveBeenCalledExactlyOnceWith(
		'session',
		expect.stringContaining('/group/snapshot?')
	);
	expect(result).toMatchObject({
		thisUeberGroup: { id: 'selected', access_right: 'own', creation_date: '2026-01-01T00:00:00Z' },
		ueberGroupCursor: 10,
		groupCursor: 12,
		allGroups: [
			{ id: 'linked', hierarchies: [{ parent_id: 'selected', child_id: 'linked' }] },
			{ id: 'available', hierarchies: [] }
		]
	});
});
test('propagates missing entity errors', async () => {
	mocks.getEntity.mockRejectedValue({ status: 404 });
	await expect(load(event as never)).rejects.toMatchObject({ status: 404 });
});
test('allows a missing creation log', async () => {
	const get = mocks.get.getMockImplementation()!;
	mocks.get.mockImplementation((session: string, path: string) =>
		path.endsWith('/created') ? new Response(null, { status: 404 }) : get(session, path)
	);
	const result = await load(event as never);
	expect(result?.thisUeberGroup.creation_date).toBeUndefined();
});
