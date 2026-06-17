// import { type AddressInfo } from "node:net";

// import {createSerer } from 'node:http';

// import { Server, type Sovcket as ServerSocket } from 'socket.io';
// import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest';
// import { describe, expect, it, vi } from 'vitest';

// // import { WebSocketServer } from 'ws';
// import { SocketIO, type SocketioConnection } from './socketioNew.svelte';

// // `vi.mock` is hoisted to the top of the file by Vitest, so the mock state it
// // references must also be defined before normal module evaluation. `vi.hoisted`
// // is the supported escape hatch. We inline the state here instead of importing
// // the `mocks/socketIoClient.ts` helper because hoisted code runs before imports
// // resolve. Keep the shape mirrored against `createSocketIoClientState` so that
// // future tests that don't need `vi.mock` can switch to the helper unchanged.
// const socketIoClient = vi.hoisted(() => {
// 	const listeners = new Map<string, Array<(...args: unknown[]) => void>>();

// 	const onImpl = (event: string, listener: (...args: unknown[]) => void) => {
// 		const existing = listeners.get(event) ?? [];
// 		existing.push(listener);
// 		listeners.set(event, existing);
// 	};

// 	const socket = {
// 		on: vi.fn(onImpl),
// 		emit: vi.fn(),
// 		connect: vi.fn(),
// 		disconnect: vi.fn()
// 	};
// 	const io = vi.fn(() => socket);

// 	const trigger = (event: string, ...args: unknown[]) => {
// 		const handlers = listeners.get(event) ?? [];
// 		for (const handler of handlers) handler(...args);
// 	};

// 	return {
// 		socket,
// 		io,
// 		listeners,
// 		trigger,
// 		reset: () => {
// 			listeners.clear();
// 			socket.on.mockReset();
// 			socket.on.mockImplementation(onImpl);
// 			socket.emit.mockReset();
// 			socket.connect.mockReset();
// 			socket.disconnect.mockReset();
// 			io.mockReset();
// 			io.mockImplementation(() => socket);
// 		}
// 	};
// });

// vi.mock('socket.io-client', () => ({
// 	io: socketIoClient.io
// }));

// vi.mock('svelte', async (importOriginal) => {
// 	const actual = await importOriginal<typeof import('svelte')>();

// 	return {
// 		...actual,
// 		getContext: vi.fn((key: unknown) => {
// 			if (key === 'backendAPIConfiguration') {
// 				return {
// 					backendFqdn: 'localhost',
// 					restApiPath: '/api/v1',
// 					websocketPath: '/ws/v1',
// 					socketIOPath: '/socketio/v1'
// 				};
// 			}

// 			// Pass through all other context keys to real Svelte behavior
// 			return actual.getContext(key as never);
// 		})
// 	};
// });

// beforeEach(() => {
// 	socketIoClient.reset();
// });

// let socketioTestServer: Server, serverSocket: ServerSocket;
// const httpServer = createServer();

// beforeAll( () => {

//     socketioTestServer = new Server(httpServer);
//      httpServer.listen(() => {
//         // const port = (httpServer.address() as AddressInfo).port;
//         socketioTestServer.on("connect", (socket: ServerSocket) => {
//             serverSocket = socket;
//         });
//     });
// });

// afterAll(() => {
// 	socketioTestServer.close();
// });

// describe('SocketIO', () => {

// 	it('connects with localhost http URL and registers the three default listeners', () => {
// 		const connection: SocketioConnection = {
// 			namespace: '/demo-resource',
// 			sessionId: 'session-123'
// 		};
// 		const cleanup = $effect.root(() => {
// 			new SocketIO(connection);
// 		});

// 		expect(console.log).toHaveBeenCalledWith('✅ Client connected');

//         // expect(serverSocket).toBeDefined();
//         // expect(serverSocket.on).toHaveBeenCalledTimes(1);

// 		// expect(socketIoClient.io).toHaveBeenCalledWith('http://localhost:1234/demo-resource', {
// 		// 	path: '/socketio/v1',
// 		// 	auth: { 'session-id': 'session-123' },
// 		// 	forceNew: true,
// 		// 	query: {}
// 		// });
// 		// expect(socketIoClient.socket.on.mock.calls.map(([event]) => event)).toEqual([
// 		// 	'transferred',
// 		// 	'deleted',
// 		// 	'status'
// 		// ]);
// 		// expect(socketIoClient.socket.connect).toHaveBeenCalledTimes(1);
// 		cleanup();
// 	});
// });

/********************************************  from Socket.io page about testing: *********** */

// import { createServer } from "node:http";
// import { type AddressInfo } from "node:net";

// import { assert } from "chai";
// import { Server, type Socket as ServerSocket } from "socket.io";
// import { io as ioc, type Socket as ClientSocket } from "socket.io-client";
// import { afterAll,  beforeAll,  describe, it } from 'vitest';

// function waitFor(socket: ServerSocket | ClientSocket, event: string) {
//   return new Promise((resolve) => {
//     socket.once(event, resolve);
//   });
// }

// describe("my awesome project", () => {
//   let io: Server, serverSocket: ServerSocket, clientSocket: ClientSocket;

//   beforeAll(() => {
//     const httpServer = createServer();
//     io = new Server(httpServer);
//     httpServer.listen(() => {
//       const port = (httpServer.address() as AddressInfo).port;
//       clientSocket = ioc(`http://localhost:${port}`);
//       io.on("connection", (socket) => {
//         serverSocket = socket;
//       });
//       clientSocket.on("connect", () => {});
//     });
//   });

//   afterAll(() => {
//     io.close();
//     clientSocket.disconnect();
//   });

//   it("should work", () => {
//     clientSocket.on("hello", (arg) => {
//       assert.equal(arg, "world");
//     });
//     serverSocket.emit("hello", "world");
//   });

//   it("should work with an acknowledgement", () => {
//     serverSocket.on("hi", (cb) => {
//       cb("hola");
//     });
//     clientSocket.emit("hi", (arg) => {
//       assert.equal(arg, "hola");
//     });
//   });

//   it("should work with emitWithAck()", async () => {
//     serverSocket.on("foo", (cb) => {
//       cb("bar");
//     });
//     const result = await clientSocket.emitWithAck("foo");
//     assert.equal(result, "bar");
//   });

//   it("should work with waitFor()", () => {
//     clientSocket.emit("baz");

//     return waitFor(serverSocket, "baz");
//   });
// });

/******************************  */

import { createServer, type Server as HttpServer } from 'node:http';
import type { AddressInfo } from 'node:net';

import { Server, type Socket as ServerSocket } from 'socket.io';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, test, vi } from 'vitest';
import { WebSocketServer } from 'ws';

import { SocketIO, type SocketioConnection } from './socketioNew.svelte';

// Mutable holder so the mocked context can expose the dynamic port chosen at listen().
let backendConfig = vi.hoisted(() => ({
	backendFqdn: 'localhost',
	restApiPath: '/api/v1',
	websocketPath: '/ws/v1',
	socketIOPath: '/socketio/v1'
}));

vi.mock('svelte', async (importOriginal) => {
	const actual = await importOriginal<typeof import('svelte')>();
	return {
		...actual,
		getContext: vi.fn((key: unknown) =>
			key === 'backendAPIConfiguration' ? backendConfig : actual.getContext(key as never)
		)
	};
});

let httpServer: HttpServer;
let socketioServer: Server;

beforeAll(async () => {
	httpServer = createServer();
	socketioServer = new Server(httpServer, {
		path: '/socketio/v1', // must match backendAPIConfiguration.socketIOPath
		wsEngine: WebSocketServer,
		cors: { origin: '*' }
	});

	// The client connects to the `/demo-resource` namespace, so register it,
	// otherwise socket.io rejects the connection as an "invalid namespace".
	socketioServer.of('/demo-resource').on('connection', () => {
		// console.log('✅ Client connected'); // your "life sign"
	});

	await new Promise<void>((resolve) => {
		httpServer.listen(() => {
			const { port } = httpServer.address() as AddressInfo;
			backendConfig = { ...backendConfig, backendFqdn: `localhost:${port}` };
			resolve();
		});
	});
	// return () => {
	// 	socketioServer.close();
	// 	httpServer.close();
	// 	console.log('✅ Test server closed');
	// }
});

afterAll(() => {
	socketioServer.close();
	httpServer.close();
	console.log('✅ Test server closed');
});

// describe('SocketIO', () => {
// 	const connection: SocketioConnection = {
// 		namespace: '/demo-resource',
// 		sessionId: 'session-123',
// 		// overrides: { transports: ['polling'] } // match the server transport
// 	};

// 	let socketio: SocketIO;
// 	let cleanup: () => void;

// 	beforeEach(async () => {
// 		cleanup = $effect.root(() => {
// 			socketio = new SocketIO(connection);
// 		});
// 		await vi.waitFor(() => expect(serverSocket).toBeDefined());
// 	});

// 	afterEach(() => {
// 		socketio.client.disconnect();
// 		cleanup();
// 	});

//     it('establishes a connection to the test server', async () => {

//         // Connection is async: the constructor returns before the socket connects.
//         await vi.waitFor(() => expect(serverSocket).toBeDefined());

//         cleanup();
//         // socketio!.client.disconnect();
//     });

// 	it('server receives submit emissions', async () => {
//     // const cleanup = $effect.root(() => { socketio = new SocketIO(connection); });
//     // await vi.waitFor(() => expect(serverSocket).toBeDefined());

//     const received = new Promise((resolve) => serverSocket!.on('submit', resolve));
//     socketio.submitEntity({ id: 'abc', name: 'x' } as never);

//     await expect(received).resolves.toMatchObject({ payload: { id: 'abc' } });
//     // cleanup();
// });
// it('stores entities sent by the server', async () => {
//     // const cleanup = $effect.root(() => { socketio = new SocketIO(connection); });
//     // await vi.waitFor(() => expect(serverSocket).toBeDefined());

//     serverSocket!.emit('transferred', { id: 'srv-1', name: 'from server' });
//     await vi.waitFor(() =>
//         expect(socketio!.entities.map((e) => e.id)).toContain('srv-1')
//     );
//     // cleanup();
// });
// });

describe('SocketIO', () => {
	const connection: SocketioConnection = {
		namespace: '/demo-resource',
		sessionId: 'session-123'
	};
	let socketio: SocketIO;
	let waitForServerConnection: Promise<ServerSocket>;
	let cleanup: () => void;

	beforeEach(async () => {

		waitForServerConnection = new Promise<ServerSocket>((resolve) => {
			socketioServer.of('/demo-resource').once('connection', (socket: ServerSocket) => {
				resolve(socket);
			});
		});

		cleanup = $effect.root(() => {
			socketio = new SocketIO(connection);
		});

		await waitForServerConnection;
	});

	afterEach(() => {
		socketio.client.disconnect();
		cleanup();
	});

	test('establishes a connection to the test server', async () => {
		const socket = await waitForServerConnection;
		expect(socket.connected).toBe(true);
	});

	test('server receives submit emissions', async () => {
		const socket = await waitForServerConnection;

		const received = new Promise((resolve) => {
			socket.once('submit', resolve);
		});

		socketio.submitEntity({ id: 'abc', name: 'x' } as never);

		await expect(received).resolves.toMatchObject({
			payload: { id: 'abc', name: 'x' }
		});
	});

	test('stores entities sent by the server', async () => {
		const socket = await waitForServerConnection;

		socket.emit('transferred', { id: 'srv-1', name: 'from server' });

		await vi.waitFor(() => {
			expect(socketio.entities.map((e) => e.id)).toContain('srv-1');
		});
	});
});
