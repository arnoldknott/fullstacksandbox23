import { beforeEach, describe, expect, test, vi } from 'vitest';

import { Action } from '$lib/accessHandler';

import { load } from './+page.server';

const backend = vi.hoisted(() => ({ get: vi.fn(), getEntity: vi.fn(), getSnapshot: vi.fn() }));
vi.mock('$lib/server/apis/backendApi', () => ({ backendAPI: backend }));

const questions = [
	{ id: 'state', question: 'cbs-presentation-state-names' },
	{ id: 'places', question: 'cbs-places' },
	{ id: 'books', question: 'cbs-books' },
	{ id: 'comments', question: 'cbs-comments' },
	{ id: 'feedback', question: 'cbs-qualitative-feedback' }
];
const event = {
	url: new URL('https://example.org/presentation/teachingengagement/cbs-2026-11'),
	locals: {}
} as Parameters<typeof load>[0];

beforeEach(() => {
	vi.clearAllMocks();
	backend.get.mockResolvedValue(new Response(JSON.stringify({ questions }), { status: 200 }));
	backend.getEntity.mockResolvedValue({ entity: { ...questions[0] }, cursor: 42 });
	backend.getSnapshot.mockResolvedValue({ entities: [], cursor: 7 });
});

describe('Presentation loading', () => {
	test.each([Action.OWN, Action.WRITE, Action.READ, Action.CONNECT])(
		'loads the effective %s right with the presenter session',
		async (accessRight) => {
			backend.get.mockImplementation(
				async (_sessionId, path) =>
					new Response(
						JSON.stringify(path === '/access/right/resource/state' ? accessRight : { questions }),
						{ status: 200 }
					)
			);
			const presenterEvent = {
				...event,
				url: new URL(`${event.url}?presenter=true`),
				locals: { sessionData: { sessionId: 'presenter-session', loggedIn: true } }
			} as unknown as typeof event;
			expect(await load(presenterEvent)).toMatchObject({
				payload: {
					presenterStateSnapshot: {
						entities: [expect.objectContaining({ access_right: accessRight })],
						cursor: 42
					}
				}
			});
			expect(backend.getEntity).toHaveBeenCalledWith('presenter-session', '/quiz/question/state');
			expect(backend.get).toHaveBeenCalledWith('presenter-session', '/access/right/resource/state');
		}
	);

	test.each([undefined, 'false', 'true'])(
		'does not read presenter rights for logged-out visitors with presenter=%s',
		async (presenter) => {
			const url = new URL(event.url);
			if (presenter) url.searchParams.set('presenter', presenter);
			await load({ ...event, url });
			expect(backend.get).toHaveBeenCalledTimes(1);
			expect(backend.getEntity).toHaveBeenCalledWith(null, '/quiz/question/state');
		}
	);

	test('leaves write permission unavailable when the effective-right request fails', async () => {
		backend.get.mockImplementation(async (_sessionId, path) =>
			path === '/access/right/resource/state'
				? new Response(null, { status: 403 })
				: new Response(JSON.stringify({ questions }), { status: 200 })
		);
		const presenterEvent = {
			...event,
			url: new URL(`${event.url}?presenter=true`),
			locals: { sessionData: { sessionId: 'presenter-session', loggedIn: true } }
		} as unknown as typeof event;
		expect(await load(presenterEvent)).toMatchObject({
			payload: {
				presenterStateSnapshot: { entities: [expect.objectContaining({ access_right: undefined })] }
			}
		});
	});

	test('starts answer snapshots without waiting for the state question', async () => {
		let resolveState!: (state: { entity: (typeof questions)[number]; cursor: number }) => void;
		backend.getEntity.mockReturnValue(
			new Promise((resolve) => {
				resolveState = resolve;
			})
		);
		const result = load(event);
		await vi.waitFor(() =>
			expect(backend.getEntity).toHaveBeenCalledWith(null, '/quiz/question/state')
		);
		try {
			expect(backend.getSnapshot).toHaveBeenCalledTimes(4);
		} finally {
			resolveState({ entity: questions[0], cursor: 42 });
		}
		expect(await result).toMatchObject({
			payload: {
				presenterStateSnapshot: { entities: [questions[0]], cursor: 42 },
				placesSnapshot: { entities: [], cursor: 7 },
				booksSnapshot: { entities: [], cursor: 7 },
				commentsSnapshot: { entities: [], cursor: 7 },
				qualitativeFeedbackSnapshot: { entities: [], cursor: 7 }
			}
		});
	});

	test('keeps an empty state snapshot when no state question exists', async () => {
		backend.get.mockResolvedValue(
			new Response(JSON.stringify({ questions: questions.slice(1) }), { status: 200 })
		);
		expect(await load(event)).toMatchObject({
			payload: {
				presenterStateSnapshot: { entities: [], cursor: 0 }
			}
		});
		expect(backend.getEntity).not.toHaveBeenCalled();
		expect(backend.getSnapshot).toHaveBeenCalledTimes(4);
	});
});
