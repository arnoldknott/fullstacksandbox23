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
	reset: () => void;
};

/**
 * Build a `socket.io-client` mock state object: a stub `io()` factory plus the
 * client it returns (`on` / `emit` / `connect` / `disconnect` are `vi.fn()`s).
 *
 * **When to use which pattern:**
 *
 * - For tests that need `vi.mock('socket.io-client', ...)` (replacing the
 *   module before any code imports it), inline the same state factory inside
 *   `vi.hoisted(...)` directly in the spec — `vi.hoisted` runs before imports
 *   resolve, so this helper cannot be imported into a hoisted block.
 * - For tests that mock at runtime (e.g. `vi.doMock`, partial mocks, or
 *   constructing a stub client passed in as a dependency), import this helper
 *   normally and call `createSocketIoClientState()`.
 *
 * Call `state.reset()` from `beforeEach` to clear call history between tests.
 */
export const createSocketIoClientState = (): SocketIoClientState => {
	const socket: MockSocketClient = {
		on: vi.fn(),
		emit: vi.fn(),
		connect: vi.fn(),
		disconnect: vi.fn()
	};
	const io = vi.fn(() => socket);

	return {
		io,
		socket,
		reset: () => {
			socket.on.mockReset();
			socket.emit.mockReset();
			socket.connect.mockReset();
			socket.disconnect.mockReset();
			io.mockReset();
			io.mockImplementation(() => socket);
		}
	};
};

