import { beforeEach, describe, expect, test, vi } from 'vitest';

import { goto } from '$app/navigation';

import { SessionLifecycle } from './session';

const session = vi.hoisted(() => ({
	loggedIn: true,
	sessionId: 'session-1',
	identityProvider: 'linkedin',
	currentUser: { linkedin_user_id: 'linkedin-1' }
}));

vi.mock('$app/navigation', () => ({ goto: vi.fn() }));
vi.mock('$app/paths', () => ({ resolve: (path: string) => path }));
vi.mock('$app/state', () => ({ page: { data: { session } } }));

describe('SessionLifecycle', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })));
	});

	test('coalesces concurrent touches and throttles all sockets through one coordinator', async () => {
		const lifecycle = new SessionLifecycle();

		await Promise.all([lifecycle.touchIfDue(), lifecycle.touchIfDue(), lifecycle.touchIfDue()]);
		await lifecycle.touchIfDue();

		expect(fetch).toHaveBeenCalledTimes(1);
		expect(fetch).toHaveBeenCalledWith('/session/touch', {
			method: 'POST',
			headers: { Authorization: 'Bearer session-1' }
		});
	});

	test('disconnects and starts provider-aware recovery after a rejected touch', async () => {
		vi.mocked(fetch).mockResolvedValueOnce(new Response(null, { status: 401 }));
		const socket = { disconnect: vi.fn() };

		await new SessionLifecycle().touchIfDue(socket as never);

		expect(socket.disconnect).toHaveBeenCalledOnce();
		expect(goto).toHaveBeenCalledWith(
			`/login/linkedin?target-url=${encodeURIComponent(window.location.href)}`
		);
	});
});
