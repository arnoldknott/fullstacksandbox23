import { createServer, type Server as HttpServer } from 'node:http';
import type { AddressInfo } from 'node:net';

import { Server, type Socket as ServerSocket } from 'socket.io';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, test, vi } from 'vitest';
import { WebSocketServer } from 'ws';

import { SocketIO, type SocketioConnection, type SocketioStatus } from './socketioNew.svelte';
// import type { AnyEntityExtended, DemoResource } from './types';
import type { DemoResource } from './types';

// Provide data for the mocked backendConfiguration. Port is filled in after the test server starts.
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
let serverSocket: ServerSocket;
let serverMessages: Array<{ event: string; data: unknown[] }> = [];

beforeAll(async () => {
	httpServer = createServer();
	socketioServer = new Server(httpServer, {
		path: '/socketio/v1', // must match backendAPIConfiguration.socketIOPath
		wsEngine: WebSocketServer,
		cors: { origin: '*' }
	});

	// The client connects to the `/demo-resource` namespace, so register it,
	// otherwise socket.io rejects the connection as an "invalid namespace".
	// socketioServer.of('/demo-resource').on('connection', () => {
	// 	// console.log('✅ Client connected'); // your "life sign"
	// });

	await new Promise<void>((resolve) => {
		httpServer.listen(() => {
			const { port } = httpServer.address() as AddressInfo;
			backendConfig = { ...backendConfig, backendFqdn: `localhost:${port}` };
			resolve();
		});
	});

	socketioServer.of('/demo-resource').on('connection', async (socket) => {
		console.log('✅ Client connected'); // your "life sign"
		serverSocket = await new Promise<ServerSocket>((resolve) => {
			resolve(socket);
		});
		serverSocket.emit('connection_ack', 'Connection established with test server');
		socket.onAny((event: string, ...data: unknown[]) => {
			console.log('Server received event:', event, 'with data:', data);
			serverMessages.push({ event, data });
		});
		socketioServer.on('disconnect', () => {
			console.log('✅ Client disconnected'); // your "life sign"
		});
	});
	// serverSocket = await new Promise<ServerSocket>((resolve) => {
	// 	socketioServer.of('/demo-resource').on('connection', (socket: ServerSocket) => {
	// 		socket.onAny((event: string, ...data: unknown[]) => {
	// 			serverMessages.push({ event, data });
	// 		});
	// 		resolve(socket);
	// 	});
	// });
});

afterAll(() => {
	serverSocket.offAny();
	socketioServer.close();
	httpServer.close();
	// console.log('✅ Test server closed');
});

// class ServerClientTestSocket<T extends AnyEntityExtended = AnyEntityExtended> {
// 	connection: SocketioConnection;

// 	// /** Promise that resolves when the socket connection
// 	//  * between the client and server is established,
// 	//  * allowing tests to wait for it before proceeding. */
// 	// #establishSocket: Promise<ServerSocket>;

// 	/** The server-side socket instance for this test socket */
// 	socket!: ServerSocket;

// 	/** Server side received messages for any event*/
// 	// serverMessages: Array<{ event: string; data: unknown[] }> = [];

// 	/** The client instance for this test socket */
// 	socketioClient!: SocketIO<T>;

// 	/** Cleanup function to disconnect the client and reset server messages */
// 	cleanup!: () => void;

// 	constructor(connection: SocketioConnection) {
// 		this.connection = connection;

// 	}

// 	static async create<T extends AnyEntityExtended = AnyEntityExtended>(connection: SocketioConnection): Promise<ServerClientTestSocket<T>> {
// 		const testSocket = new ServerClientTestSocket<T>(connection);
// 		// const establishSocket = new Promise<ServerSocket>((resolve) => {
// 		// 	socketioServer.of('/demo-resource').once('connection', (socket: ServerSocket) => {
// 		// 		socket.onAny((event: string, ...data: unknown[]) => {
// 		// 			testSocket.serverMessages.push({ event, data });
// 		// 		});
// 		// 		resolve(socket);
// 		// 	});
// 		// });

// 		testSocket.cleanup = $effect.root(() => {
// 			testSocket.socketioClient = new SocketIO(connection);
// 		});

// 		// testSocket.socket = await establishSocket;
// 		return testSocket;
// 	}

// 	disconnect(): void {
// 		this.socket.offAny();
// 		this.socketioClient.client.disconnect();
// 		// this.serverMessages = [];
// 		this.cleanup();
// 	}
// }

describe('SocketIO for DemoResources', () => {
	const connection: SocketioConnection = {
		namespace: '/demo-resource',
		sessionId: 'session-123'
	};
	// let serverSocket: ServerSocket;
	let socketioClient: SocketIO<DemoResource>;
	// let serverMessages: Array<{ event: string; data: unknown[] }> = [];
	// let waitForServerConnection: Promise<ServerSocket>;
	// let onAnyHandler: ((event: string, ...args: unknown[]) => void) | undefined;
	let cleanup: () => void;

	beforeEach(async () => {
		serverMessages = [];

		// // waitForServerConnection = new Promise<ServerSocket>((resolve) => {
		// 	socketioServer.of('/demo-resource').once('connection', (socket: ServerSocket) => {
		// 		// onAnyHandler = ((event: string, ...data: unknown[]) => {
		// 		socket.onAny ((event: string, ...data: unknown[]) => {
		// 			serverMessages.push({ event, data });
		// 		});
		// 		// socket.onAny(onAnyHandler);
		// 		resolve(socket);
		// 	});
		// });

		// const connectionPromise=  new Promise<ServerSocket>((resolve) => {
		// 	socketioServer.of('/demo-resource').once('connection', (socket: ServerSocket) => {
		// 		socket.onAny((event: string, ...data: unknown[]) => {
		// 			serverMessages.push({ event, data });
		// 		});
		// 		resolve(socket);
		// 	});
		// });

		cleanup = $effect.root(() => {
			socketioClient = new SocketIO(connection);
		});
		await new Promise<void>((resolve) => {
			socketioClient.client.on('connection_ack', (_message: string) => {
				resolve();
			});
		});

		// serverSocket = await connectionPromise;
		// serverSocket = await waitForServerConnection;
	});

	afterEach(() => {
		// if (onAnyHandler) {
		// serverSocket.offAny();
		// }
		socketioClient.client.disconnect();
		serverMessages = [];
		cleanup();
	});

	// region: Tests for constructor:
	// - instantiation
	// - default handler behavior

	test('establishes a connection to the test server', async () => {
		expect(serverSocket.connected).toBe(true);
	});

	test('uses default handlers when no overrides are provided', async () => {
		const emitSpy = vi.spyOn(socketioClient.client, 'emit');

		// Seed one entity so deleted/status behavior is observable
		socketioClient.entities = [{ id: 'seed', name: 'seed' } as never];

		// 1) transferred default handler should add/update entities
		serverSocket.emit('transferred', { id: 'srv-1', name: 'from server' });
		await vi.waitFor(() => {
			expect(socketioClient.entities.map((e) => e.id)).toContain('srv-1');
		});

		// 2) deleted default handler should remove entity by id
		serverSocket.emit('deleted', 'srv-1');
		await vi.waitFor(() => {
			expect(socketioClient.entities.map((e) => e.id)).not.toContain('srv-1');
		});

		// 3) status default handler should trigger read on shared/unshared
		serverSocket.emit('status', { success: 'shared', id: 'seed' });
		await vi.waitFor(() => {
			expect(emitSpy).toHaveBeenCalledWith('read', 'seed');
		});
	});

	test('disables  default handlers when specified in options', async () => {
		cleanup();
		socketioClient = new SocketIO(connection, {
			transferred: false,
			deleted: false,
			status: false
		});

		const emitSpy = vi.spyOn(socketioClient.client, 'emit');
		// Seed one entity so deleted/status behavior is observable
		socketioClient.entities = [{ id: 'seed', name: 'seed' } as never];

		// transferred handler should be overridden to do nothing
		serverSocket.emit('transferred', { id: 'srv-1', name: 'from server' });
		await vi.waitFor(() => {
			expect(socketioClient.entities.map((e) => e.id)).not.toContain('srv-1');
		});

		// deleted handler should be overridden to do nothing
		serverSocket.emit('deleted', 'seed');
		await vi.waitFor(() => {
			expect(socketioClient.entities.map((e) => e.id)).toContain('seed');
		});

		// status handler should be overridden to do nothing
		serverSocket.emit('status', { success: 'shared', id: 'seed' });
		await vi.waitFor(() => {
			expect(emitSpy).not.toHaveBeenCalledWith('read', 'seed');
		});
	});

	test('overrides default handlers with custom implementations', async () => {
		cleanup();
		socketioClient.client.disconnect();

		const newConnection = new Promise<ServerSocket>((resolve) => {
			socketioServer.of('/demo-resource').once('connection', (socket: ServerSocket) => {
				resolve(socket);
			});
		});
		socketioClient = new SocketIO(connection, {
			transferred: (data) => {
				console.log('custom transferred', data);
			},
			deleted: (id) => {
				console.log('custom deleted', id);
			},
			status: (status) => {
				console.log('custom status', status);
			}
		});
		serverSocket = await newConnection;

		const logSpy = vi.spyOn(console, 'log');

		serverSocket.emit('transferred', { id: 'srv-1', name: 'from server' });
		await vi.waitFor(() => {
			expect(logSpy).toHaveBeenCalledWith('custom transferred', {
				id: 'srv-1',
				name: 'from server'
			});
		});

		serverSocket.emit('deleted', 'srv-1');
		await vi.waitFor(() => {
			expect(logSpy).toHaveBeenCalledWith('custom deleted', 'srv-1');
		});

		const status = { success: 'shared', id: 'srv-1' } as SocketioStatus;
		serverSocket.emit('status', status);
		await vi.waitFor(() => {
			expect(logSpy).toHaveBeenCalledWith('custom status', status);
		});
	});

	test('server receives submit emissions', async () => {
		socketioClient.submitEntity({ id: 'abc', name: 'x' } as never);

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'submit',
			data: [expect.objectContaining({ payload: { id: 'abc', name: 'x' } })]
		});
	});

	test('stores entities sent by the server', async () => {
		serverSocket.emit('transferred', { id: 'srv-1', name: 'from server' });

		await vi.waitFor(() => {
			expect(socketioClient.entities.map((e) => e.id)).toContain('srv-1');
			expect(socketioClient.entities.map((e) => e.name)).toContain('from server');
		});
	});

	// endregion: Tests for constructor

	// region: Tests for Submit Event Emitters:

	test('submitEntity emits "submit" event with correct payload', async () => {
		socketioClient.submitEntity({ id: 'abc', name: 'x' } as never);

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'submit',
			data: [expect.objectContaining({ payload: { id: 'abc', name: 'x' } })]
		});
	});

	test('submitEntity auto-submits pending entity when pendingTemplate is set and no entity is provided for submission', async () => {
		socketioClient.pendingTemplate = { name: 'pending' };
		socketioClient.createPending() as DemoResource; // Create a pending entity to trigger auto-submit
		socketioClient.createPending = vi.fn(socketioClient.createPending); // Spy on createPending to verify it's called

		socketioClient.submitEntity();

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'submit',
			data: [expect.objectContaining({ payload: expect.objectContaining({ name: 'pending' }) })]
		});
		expect(socketioClient.createPending).toHaveBeenCalledTimes(1);
	});

	test('submitEntity does not auto-submit when pendingTemplate is set but an entity is provided for submission', async () => {
		socketioClient.pendingTemplate = { name: 'pending' };

		socketioClient.submitEntity({ id: 'abc', name: 'x' } as never);

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'submit',
			data: [expect.objectContaining({ payload: { id: 'abc', name: 'x' } })]
		});
		expect(serverMessages).not.toContainEqual({
			event: 'submit',
			data: [expect.objectContaining({ payload: expect.objectContaining({ name: 'pending' }) })]
		});
	});

	// endregion: Tests for Submit Event Emitters
});
