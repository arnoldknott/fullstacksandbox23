import { describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({ post: vi.fn() }));

vi.mock('$lib/server/apis/backendApi', () => ({
	backendAPI: { post: mocks.post }
}));

import { POST } from './+server';

describe('POST /api/v1/socketio-ticket', () => {
	test('uses the authenticated server session without exposing it in the response', async () => {
		mocks.post.mockResolvedValue(
			new Response(JSON.stringify({ ticket: 'short-lived-ticket' }), { status: 200 })
		);

		const response = await POST({
			locals: { sessionData: { sessionId: 'reusable-session-reference' } }
		} as never);

		expect(mocks.post).toHaveBeenCalledWith(
			'reusable-session-reference',
			'/core/socketio-ticket',
			'{}'
		);
		expect(await response.json()).toEqual({ ticket: 'short-lived-ticket' });
	});
});
