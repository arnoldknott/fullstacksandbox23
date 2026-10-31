import { beforeEach, describe, expect, test, vi } from 'vitest';

import { goto } from '$app/navigation';

import { SessionLifecycle } from './session';

const session = vi.hoisted(() => ({
	loggedIn: true,
	sessionId: 'session-1',
	sessionOwnerProvider: 'linkedin',
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

	test('captures the exact presenter slide and fragment once across multiple expired sockets', () => {
		const originalUrl = window.location.href;
		window.history.replaceState(
			{},
			'',
			'/presentation/teachingengagement/cbs-2026-11?presenter=true#/inspiration-books/2'
		);
		try {
			const lifecycle = new SessionLifecycle();
			const sockets = [{ disconnect: vi.fn() }, { disconnect: vi.fn() }];
			for (const socket of sockets) lifecycle.reauthenticate(socket as never);

			expect(goto).toHaveBeenCalledOnce();
			const loginUrl = new URL(vi.mocked(goto).mock.calls[0][0], window.location.origin);
			expect(loginUrl.searchParams.get('target-url')).toBe(window.location.href);
			for (const socket of sockets) expect(socket.disconnect).toHaveBeenCalledOnce();
		} finally {
			window.history.replaceState({}, '', originalUrl);
		}
	});

	test('captures live presentation state before its debounced URL update', () => {
		const lifecycle = new SessionLifecycle();
		const target = `${window.location.origin}/presentation/cbs?presenter=true#/inspiration-books/1`;
		const unregister = lifecycle.registerReauthenticationTarget(() => target);
		lifecycle.reauthenticate({ disconnect: vi.fn() } as never);
		expect(goto).toHaveBeenCalledWith(`/login/linkedin?target-url=${encodeURIComponent(target)}`);
		unregister();
	});

	test('removes the presentation-specific return target when the presentation unmounts', () => {
		const lifecycle = new SessionLifecycle();
		const unregister = lifecycle.registerReauthenticationTarget(() => 'https://stale.example/');
		unregister();
		lifecycle.reauthenticate({ disconnect: vi.fn() } as never);
		expect(goto).toHaveBeenCalledWith(
			`/login/linkedin?target-url=${encodeURIComponent(window.location.href)}`
		);
	});
});
