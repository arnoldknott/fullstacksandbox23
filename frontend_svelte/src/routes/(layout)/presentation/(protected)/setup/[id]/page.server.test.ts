import { beforeEach, describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	get: vi.fn(),
	getSnapshot: vi.fn(),
	getEntity: vi.fn(),
	getAccessPolicies: vi.fn()
}));

vi.mock('$lib/server/apis/backendApi', () => ({
	backendAPI: { ...mocks, getAllIdentities: vi.fn().mockResolvedValue([]) }
}));
vi.mock('$lib/server/apis/msgraph', () => ({
	microsoftGraph: { getAttachedTeamsAsIdentities: vi.fn().mockResolvedValue([]) }
}));

import { load } from './+page.server';

const presentationPath = '/presentation/presentation-1';
const policiesPath = '/access/policy/resource/presentation-1';
const rightPath = '/access/right/resource/presentation-1';
const policy = { resource_id: 'presentation-1', identity_id: 'group-1', action: 'write' };
const event = {
	params: { id: 'presentation-1' },
	locals: { sessionData: { sessionId: 'session-1' } }
};

const presentationResult = () => ({
	entity: { id: 'presentation-1', path: '/example' },
	cursor: 21
});

describe('presentation setup resource-specific loading', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.getEntity.mockResolvedValue(presentationResult());
		mocks.getAccessPolicies.mockResolvedValue([]);
		mocks.getSnapshot.mockResolvedValue({ entities: [{ id: 'question-1' }], cursor: 42 });
		mocks.get.mockImplementation((_sessionId: string, path: string) => {
			if (path === policiesPath) return Promise.resolve(Response.json([policy]));
			if (path === rightPath) return Promise.resolve(Response.json('own'));
			return Promise.resolve(Response.json([]));
		});
	});

	test('loads only the selected presentation and its access data with a separate replay cursor', async () => {
		const result = await load(event as never);
		if (!result) throw new Error('Presentation setup load returned no data.');
		expect(result.payload.presentation).toMatchObject({
			id: 'presentation-1',
			access_right: 'own',
			access_policies: [policy]
		});
		expect(mocks.getEntity).toHaveBeenCalledWith('session-1', presentationPath);
		expect(mocks.getAccessPolicies).toHaveBeenCalledWith('session-1', ['question-1']);
		expect(result.payload.presentationCursor).toBe(21);
		expect(result.payload.cursor).toBe(42);
		expect(result.payload.questions[0].access_policies).toEqual([]);
		for (const path of [policiesPath, rightPath]) {
			expect(mocks.get).toHaveBeenCalledWith('session-1', path);
		}
		expect(mocks.getSnapshot).toHaveBeenCalledTimes(1);
		expect(mocks.getSnapshot).toHaveBeenCalledWith(
			'session-1',
			expect.stringContaining('/quiz/question/snapshot?')
		);
		expect(mocks.get).not.toHaveBeenCalledWith(
			expect.anything(),
			'/access/policy/resource/type/Presentation'
		);
	});

	test.each([policiesPath, rightPath])(
		'propagates a failed resource-specific request: %s',
		async (failedPath) => {
			const successfulGet = mocks.get.getMockImplementation()!;
			mocks.get.mockImplementation((sessionId: string, path: string) =>
				path === failedPath
					? Promise.resolve(new Response(null, { status: 403 }))
					: successfulGet(sessionId, path)
			);
			await expect(load(event as never)).rejects.toMatchObject({ status: 403 });
		}
	);

	test('preserves presentation not-found responses', async () => {
		mocks.getEntity.mockRejectedValue({ status: 404 });
		await expect(load(event as never)).rejects.toMatchObject({ status: 404 });
	});

	test('loads access data only after the presentation read has captured its replay cursor', async () => {
		let resolvePresentation!: (value: ReturnType<typeof presentationResult>) => void;
		mocks.getEntity.mockImplementation(
			() => new Promise((resolve) => (resolvePresentation = resolve))
		);
		const loading = load(event as never);
		expect(mocks.get).not.toHaveBeenCalledWith('session-1', policiesPath);
		resolvePresentation(presentationResult());
		await loading;
		expect(mocks.get).toHaveBeenCalledWith('session-1', policiesPath);
	});
});
