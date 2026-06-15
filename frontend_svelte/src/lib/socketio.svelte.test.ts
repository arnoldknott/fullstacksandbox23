import { beforeEach, describe, expect, it, vi } from 'vitest';

import { SocketIO, type SocketioConnection } from './socketioNew.svelte';

// `vi.mock` is hoisted to the top of the file by Vitest, so the mock state it
// references must also be defined before normal module evaluation. `vi.hoisted`
// is the supported escape hatch. We inline the state here instead of importing
// the `mocks/socketIoClient.ts` helper because hoisted code runs before imports
// resolve. Keep the shape mirrored against `createSocketIoClientState` so that
// future tests that don't need `vi.mock` can switch to the helper unchanged.
const socketIoClient = vi.hoisted(() => {
	const listeners = new Map<string, Array<(...args: unknown[]) => void>>();

	const onImpl = (event: string, listener: (...args: unknown[]) => void) => {
		const existing = listeners.get(event) ?? [];
		existing.push(listener);
		listeners.set(event, existing);
	};

	const socket = {
		on: vi.fn(onImpl),
		emit: vi.fn(),
		connect: vi.fn(),
		disconnect: vi.fn()
	};
	const io = vi.fn(() => socket);

	const trigger = (event: string, ...args: unknown[]) => {
		const handlers = listeners.get(event) ?? [];
		for (const handler of handlers) handler(...args);
	};

	return {
		socket,
		io,
		listeners,
		trigger,
		reset: () => {
			listeners.clear();
			socket.on.mockReset();
			socket.on.mockImplementation(onImpl);
			socket.emit.mockReset();
			socket.connect.mockReset();
			socket.disconnect.mockReset();
			io.mockReset();
			io.mockImplementation(() => socket);
		}
	};
});

vi.mock('socket.io-client', () => ({
	io: socketIoClient.io
}));

vi.mock('svelte', async (importOriginal) => {
	const actual = await importOriginal<typeof import('svelte')>();

	return {
		...actual,
		getContext: vi.fn((key: unknown) => {
			if (key === 'backendAPIConfiguration') {
				return {
					backendFqdn: 'localhost:1234',
					restApiPath: '/api/v1',
					websocketPath: '/ws/v1',
					socketIOPath: '/socketio/v1'
				};
			}

			// Pass through all other context keys to real Svelte behavior
			return actual.getContext(key as never);
		})
	};
});

beforeEach(() => {
	socketIoClient.reset();
});

describe('SocketIO', () => {
	it('connects with localhost http URL and registers the three default listeners', () => {
		const connection: SocketioConnection = {
			namespace: '/demo-resource',
			sessionId: 'session-123'
		};
		const cleanup = $effect.root(() => {
			new SocketIO(connection);
		});

		expect(socketIoClient.io).toHaveBeenCalledWith('http://localhost:1234/demo-resource', {
			path: '/socketio/v1',
			auth: { 'session-id': 'session-123' },
			forceNew: true,
			query: {}
		});
		expect(socketIoClient.socket.on.mock.calls.map(([event]) => event)).toEqual([
			'transferred',
			'deleted',
			'status'
		]);
		// expect(socketIoClient.socket.connect).toHaveBeenCalledTimes(1);
		cleanup();
	});
});
