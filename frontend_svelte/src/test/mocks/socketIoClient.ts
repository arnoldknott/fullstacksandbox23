import { vi } from 'vitest';

export type MockSocketClient = {
	on: ReturnType<typeof vi.fn>;
	emit: ReturnType<typeof vi.fn>;
	connect: ReturnType<typeof vi.fn>;
	disconnect: ReturnType<typeof vi.fn>;
};

export type SocketIoClientState = {
	io: ReturnType<typeof vi.fn>;
	socket: MockSocketClient;
	/** Listeners registered via `socket.on(event, listener)`, grouped by event. */
	listeners: Map<string, Array<(...args: unknown[]) => void>>;
	/** Invoke every listener registered for `event` with the supplied args. */
	trigger: (event: string, ...args: unknown[]) => void;
	/** Reset all `vi.fn`s and the listener registry. */
	reset: () => void;
};

/**
 * Build a `socket.io-client` mock state object: a stub `io()` factory plus the
 * client it returns (`on` / `emit` / `connect` / `disconnect` are `vi.fn()`s).
 *
 * Listeners registered through `socket.on(...)` are captured in `listeners`
 * and can be fired back via `state.trigger(event, ...args)` to simulate
 * inbound events from a server.
 *
 * **When to use which pattern:**
 *
 * - For tests that need `vi.mock('socket.io-client', ...)` (replacing the
 *   module before any code imports it), inline an equivalent state factory
 *   inside `vi.hoisted(...)` directly in the spec — `vi.hoisted` runs before
 *   imports resolve, so this helper cannot be imported into a hoisted block.
 *   Mirror the shape exposed here so future migration is mechanical.
 * - For tests that mock at runtime (e.g. `vi.doMock`, partial mocks, or
 *   constructing a stub client passed in as a dependency), import this helper
 *   normally and call `createSocketIoClientState()`.
 *
 * Call `state.reset()` from `beforeEach` to clear call history between tests.
 */
export const createSocketIoClientState = (): SocketIoClientState => {
	const listeners = new Map<string, Array<(...args: unknown[]) => void>>();

	const socket: MockSocketClient = {
		on: vi.fn((event: string, listener: (...args: unknown[]) => void) => {
			const existing = listeners.get(event) ?? [];
			existing.push(listener);
			listeners.set(event, existing);
		}),
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
		io,
		socket,
		listeners,
		trigger,
		reset: () => {
			listeners.clear();
			socket.on.mockReset();
			socket.on.mockImplementation((event: string, listener: (...args: unknown[]) => void) => {
				const existing = listeners.get(event) ?? [];
				existing.push(listener);
				listeners.set(event, existing);
			});
			socket.emit.mockReset();
			socket.connect.mockReset();
			socket.disconnect.mockReset();
			io.mockReset();
			io.mockImplementation(() => socket);
		}
	};
};


