import { createServer, type Server as HttpServer } from 'node:http';
import type { AddressInfo } from 'node:net';

import { Server, type Socket as ServerSocket } from 'socket.io';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, test, vi } from 'vitest';
import { WebSocketServer } from 'ws';

import { SocketIO, type SocketioConnection, type SocketioStatus } from './socketioNew.svelte';
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
});

afterAll(() => {
	socketioServer.close();
	httpServer.close();
	// console.log('✅ Test server closed');
});

describe('SocketIO for DemoResources', () => {
	const connection: SocketioConnection = {
		namespace: '/demo-resource',
		sessionId: 'session-123'
	};
	let serverSocket: ServerSocket;
	let socketioClient: SocketIO<DemoResource>;
	let serverMessages: Array<{ event: string; data: unknown[] }> = [];
	let waitForServerConnection: Promise<ServerSocket>;
	let onAnyHandler: ((event: string, ...args: unknown[]) => void) | undefined;
	let cleanup: () => void;

	beforeEach(async () => {
		serverMessages = [];

		waitForServerConnection = new Promise<ServerSocket>((resolve) => {
			socketioServer.of('/demo-resource').once('connection', (socket: ServerSocket) => {
				onAnyHandler = (event: string, ...data: unknown[]) => {
					serverMessages.push({ event, data });
				};
				socket.onAny(onAnyHandler);
				resolve(socket);
			});
		});

		cleanup = $effect.root(() => {
			socketioClient = new SocketIO(connection);
		});

		serverSocket = await waitForServerConnection;
	});

	afterEach(() => {
		if (onAnyHandler) {
			serverSocket.offAny(onAnyHandler);
		}
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
			expect(serverMessages.length).toBeGreaterThan(0);
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
});
