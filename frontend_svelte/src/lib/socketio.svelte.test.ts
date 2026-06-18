import { createServer, type Server as HttpServer } from 'node:http';
import type { AddressInfo } from 'node:net';

import { Server, type Socket as ServerSocket } from 'socket.io';
import { afterAll, beforeAll, beforeEach, describe, expect, test, vi } from 'vitest';
import { WebSocketServer } from 'ws';

import { SocketIO, type SocketioConfiguration, type SocketioConnection, type SocketioStatus } from './socketioNew.svelte';
import type { AnyEntityExtended, DemoResource } from './types';

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

	// For debuging the connection - server can console.log an established connection:
	// socketioServer.of('/demo-resource').on('connection', () => {
	// 	// console.log('✅ Client connected');
	// });

	await new Promise<void>((resolve) => {
		httpServer.listen(() => {
			const { port } = httpServer.address() as AddressInfo;
			backendConfig = { ...backendConfig, backendFqdn: `localhost:${port}` };
			resolve();
		});
	});

	socketioServer.of('/demo-resource').on('connection', async (socket) => {
		// console.log('✅ Client connected'); // your "life sign"
		serverSocket = await new Promise<ServerSocket>((resolve) => {
			resolve(socket);
		});
		serverSocket.emit('connection_ack', 'Connection established with test server');
		socket.onAny((event: string, ...data: unknown[]) => {
			// For debugging - server side logging of the received data:
			// console.log('Server received event:', event, 'with data:', data);
			serverMessages.push({ event, data });
		});
		// For debuging the connection - server can console.log a disconnect:
		// socket.on('disconnect', () => {
			// console.log('✅ Client disconnected'); // your "life sign"
		// });
	});
});

afterAll(() => {
	serverSocket.offAny();
	socketioServer.close();
	httpServer.close();
	// console.log('✅ Test server closed');
});

class SocketioClientHandler<T extends AnyEntityExtended = AnyEntityExtended> {
	connection: SocketioConnection;

	/** The client instance for this test socket */
	socketioClient!: SocketIO<T>;

	/** Cleanup function to disconnect the client and reset server messages */
	cleanup!: () => void;

	constructor(connection: SocketioConnection) {
		this.connection = connection;
	}

	static async create<T extends AnyEntityExtended = AnyEntityExtended>(
		connection: SocketioConnection, configuration: SocketioConfiguration<T> = {}
	): Promise<SocketioClientHandler<T>> {
		serverMessages = [];
		const testSocket = new SocketioClientHandler<T>(connection);

		testSocket.cleanup = $effect.root(() => {
			testSocket.socketioClient = new SocketIO(connection, configuration);
		});

		await new Promise<void>((resolve) => {
			testSocket.socketioClient.client.on('connection_ack', (_message: string) => {
				resolve();
			});
		});

		return testSocket;
	}

	disconnect(): void {
		this.socketioClient.client.disconnect();
		serverMessages = [];
		this.cleanup();
	}
}

describe('SocketIO for DemoResources', () => {
	let socketioClientHandler: SocketioClientHandler;
	let testSocketio: SocketIO<DemoResource>;

	beforeEach(async () => {
		socketioClientHandler = await SocketioClientHandler.create<DemoResource>({
			namespace: '/demo-resource',
			sessionId: 'session-123'
		});
		testSocketio = socketioClientHandler.socketioClient as SocketIO<DemoResource>;
		return(() => {
			testSocketio.client.disconnect();
			serverMessages = [];
		});
	});

	// region: Tests for constructor:
	// - instantiation
	// - default handler behavior

	test('establishes a connection to the test server', async () => {
		expect(serverSocket.connected).toBe(true);
	});

	test('uses default handlers when no overrides are provided', async () => {
		const emitSpy = vi.spyOn(testSocketio.client, 'emit');

		// Seed one entity so deleted/status behavior is observable
		testSocketio.entities = [{ id: 'seed', name: 'seed' } as never];

		// 1) transferred default handler should add/update entities
		serverSocket.emit('transferred', { id: 'srv-1', name: 'from server' });
		await vi.waitFor(() => {
			expect(testSocketio.entities.map((e) => e.id)).toContain('srv-1');
		});

		// 2) deleted default handler should remove entity by id
		serverSocket.emit('deleted', 'srv-1');
		await vi.waitFor(() => {
			expect(testSocketio.entities.map((e) => e.id)).not.toContain('srv-1');
		});

		// 3) status default handler should trigger read on shared/unshared
		serverSocket.emit('status', { success: 'shared', id: 'seed' });
		await vi.waitFor(() => {
			expect(emitSpy).toHaveBeenCalledWith('read', 'seed');
		});
	});

	test('disables  default handlers when specified in options', async () => {
		const clientHandler = await SocketioClientHandler.create<DemoResource>({
			namespace: '/demo-resource',
			sessionId: 'session-123'
		}, {
			transferred: false,
			deleted: false,
			status: false
		});
		const testClientWithDefaultHandlersDisabled = clientHandler.socketioClient;

		const emitSpy = vi.spyOn(testClientWithDefaultHandlersDisabled.client, 'emit');
		// Seed one entity so deleted/status behavior is observable
		testClientWithDefaultHandlersDisabled.entities = [{ id: 'seed', name: 'seed' } as never];

		// transferred handler should be overridden to do nothing
		serverSocket.emit('transferred', { id: 'srv-1', name: 'from server' });
		await vi.waitFor(() => {
			expect(testClientWithDefaultHandlersDisabled.entities.map((e) => e.id)).not.toContain('srv-1');
		});

		// deleted handler should be overridden to do nothing
		serverSocket.emit('deleted', 'seed');
		await vi.waitFor(() => {
			expect(testClientWithDefaultHandlersDisabled.entities.map((e) => e.id)).toContain('seed');
		});

		// status handler should be overridden to do nothing
		serverSocket.emit('status', { success: 'shared', id: 'seed' });
		await vi.waitFor(() => {
			expect(emitSpy).not.toHaveBeenCalledWith('read', 'seed');
		});

		clientHandler.disconnect();
	});

	test('overrides default handlers with custom implementations', async () => {
		const overridesCalled = {
			transferred: false as boolean | DemoResource,
			deleted: false as boolean | string,
			status: false as boolean | SocketioStatus
		};

		const clientHandler = await SocketioClientHandler.create<DemoResource>({
			namespace: '/demo-resource',
			sessionId: 'session-123'
		}, {
			transferred:(data) => {
				overridesCalled.transferred = data;
			},
			deleted: (id) => {
				overridesCalled.deleted = id;
			},
			status: (status) => {
				overridesCalled.status = status;
			}
		});

		serverSocket.emit('transferred', { id: 'srv-1', name: 'from server' });
		await vi.waitFor(() => {
			expect(overridesCalled.transferred).toEqual({ id: 'srv-1', name: 'from server' });
		});
		expect(overridesCalled.transferred).toEqual({ id: 'srv-1', name: 'from server' });
		
		serverSocket.emit('deleted', 'srv-1');
		await vi.waitFor(() => {
			expect(overridesCalled.deleted).toEqual('srv-1');
		});

		const status = { success: 'shared', id: 'srv-1' } as SocketioStatus;
		serverSocket.emit('status', status);
		await vi.waitFor(() => {
			expect(overridesCalled.status).toEqual(status);
		});

		clientHandler.disconnect();
	});

	test('server receives submit emissions', async () => {
		testSocketio.submitEntity({ id: 'abc', name: 'x' } as never);

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
			expect(testSocketio.entities.map((e) => e.id)).toContain('srv-1');
			expect(testSocketio.entities.map((e) => e.name)).toContain('from server');
		});
	});

	// endregion: Tests for constructor

	// region: Tests for Submit Event Emitters:

	test('submitEntity emits "submit" event with correct payload', async () => {
		testSocketio.submitEntity({ id: 'abc', name: 'x' } as never);

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'submit',
			data: [expect.objectContaining({ payload: { id: 'abc', name: 'x' } })]
		});
	});

	test('submitEntity auto-submits pending entity when pendingTemplate is set and no entity is provided for submission', async () => {
		testSocketio.pendingTemplate = { name: 'pending' };
		testSocketio.createPending() as DemoResource; // Create a pending entity to trigger auto-submit
		testSocketio.createPending = vi.fn(testSocketio.createPending); // Spy on createPending to verify it's called

		testSocketio.submitEntity();

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'submit',
			data: [expect.objectContaining({ payload: expect.objectContaining({ name: 'pending' }) })]
		});
		expect(testSocketio.createPending).toHaveBeenCalledTimes(1);
	});

	test('submitEntity does not auto-submit when pendingTemplate is set but an entity is provided for submission', async () => {
		testSocketio.pendingTemplate = { name: 'pending' };

		testSocketio.submitEntity({ id: 'abc', name: 'x' } as never);

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
