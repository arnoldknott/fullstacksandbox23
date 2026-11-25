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

const response = (body: unknown, status = 200) =>
	new Response(JSON.stringify(body), {
		status,
		headers: { 'content-type': 'application/json' }
	});

describe('question setup snapshot', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.getEntity.mockResolvedValue({ entity: { id: 'question-1' }, cursor: 10 });
		mocks.getAccessPolicies.mockResolvedValue([
			{ id: 3, resource_id: 'question-1', action: 'own', public: false },
			{ id: 1, resource_id: 'message-1', action: 'own', public: false },
			{ id: 2, resource_id: 'numerical-1', action: 'write', public: false }
		]);
		mocks.getSnapshot.mockImplementation((_sessionId: string, path: string) => {
			if (path.startsWith('/quiz/message/snapshot')) {
				return Promise.resolve({
					entities: [{ id: 'message-1', access_right: 'own' }],
					cursor: 11
				});
			}
			return Promise.resolve({
				entities: [{ id: 'numerical-1', access_right: 'write' }],
				cursor: 12
			});
		});
		mocks.get.mockResolvedValue(
			response([
				{ parent_id: 'question-1', child_id: 'message-1', inherit: true, order: 1 },
				{ parent_id: 'question-1', child_id: 'numerical-1', inherit: false, order: 2 }
			])
		);
	});

	test('restores extended access data before seeding Socket.IO', async () => {
		const result = await load({
			params: { id: 'question-1' },
			locals: { sessionData: { sessionId: 'session-1' } }
		} as never);
		if (!result) throw new Error('Question setup load returned no data.');

		expect(mocks.getSnapshot).toHaveBeenCalledWith(
			'session-1',
			expect.stringContaining(
				'include=creation-date&include=last-modified-date&include=access-right'
			)
		);
		expect(mocks.getEntity).toHaveBeenCalledWith('session-1', '/quiz/question/question-1');
		expect(mocks.getAccessPolicies).toHaveBeenCalledWith('session-1', [
			'question-1',
			'message-1',
			'numerical-1'
		]);
		expect(result.questionsData.questions.access_policies).toEqual([
			{ id: 3, resource_id: 'question-1', action: 'own', public: false }
		]);
		expect(result.questionsData.questionCursor).toBe(10);
		expect(result.questionsData.identities.at(-1)).toMatchObject({ id: 'public' });
		expect(result.questionsData.messages[0]).toMatchObject({
			id: 'message-1',
			access_right: 'own',
			access_policies: [{ id: 1, resource_id: 'message-1', action: 'own', public: false }],
			hierarchies: [{ parent_id: 'question-1', child_id: 'message-1', inherit: true, order: 1 }]
		});
		expect(result.questionsData.numericals[0]).toMatchObject({
			id: 'numerical-1',
			access_right: 'write',
			access_policies: [{ id: 2, resource_id: 'numerical-1', action: 'write', public: false }],
			hierarchies: [{ parent_id: 'question-1', child_id: 'numerical-1', inherit: false, order: 2 }]
		});
	});
});
