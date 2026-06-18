import { createServer, type Server as HttpServer } from 'node:http';
import type { AddressInfo } from 'node:net';

import { Server, type Socket as ServerSocket } from 'socket.io';
import { afterAll, beforeAll, beforeEach, describe, expect, test, vi } from 'vitest';
import { WebSocketServer } from 'ws';

import {
	SocketIO,
	type SocketioConfiguration,
	type SocketioConnection,
	type SocketioStatus
} from './socketio.svelte';
import type { AccessPolicy, AnyEntityExtended, DemoResource } from './types';

// #region: Setup Test Socketio Server

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

// #endregion: Setup Test Socketio Client

// #region: Setup Test Socketio Client

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
		connection: SocketioConnection,
		configuration: SocketioConfiguration<T> = {}
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

// #endregion: Setup Test Socketio Client

describe('SocketIO for DemoResources', () => {
	let socketioClientHandler: SocketioClientHandler;
	let testSocketio: SocketIO<DemoResource>;
	const parentId = 'parent-from-describe';

	beforeEach(async () => {
		socketioClientHandler = await SocketioClientHandler.create<DemoResource>({
			namespace: '/demo-resource',
			sessionId: 'session-123',
			parentId: parentId
		});
		testSocketio = socketioClientHandler.socketioClient as SocketIO<DemoResource>;
		return () => {
			testSocketio.client.disconnect();
			serverMessages = [];
		};
	});

	// #region: Tests for constructor

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
		const clientHandler = await SocketioClientHandler.create<DemoResource>(
			{
				namespace: '/demo-resource',
				sessionId: 'session-123'
			},
			{
				transferred: false,
				deleted: false,
				status: false
			}
		);
		const testClientWithDefaultHandlersDisabled = clientHandler.socketioClient;

		const emitSpy = vi.spyOn(testClientWithDefaultHandlersDisabled.client, 'emit');
		// Seed one entity so deleted/status behavior is observable
		testClientWithDefaultHandlersDisabled.entities = [{ id: 'seed', name: 'seed' } as never];

		// transferred handler should be overridden to do nothing
		serverSocket.emit('transferred', { id: 'srv-1', name: 'from server' });
		await vi.waitFor(() => {
			expect(testClientWithDefaultHandlersDisabled.entities.map((e) => e.id)).not.toContain(
				'srv-1'
			);
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

		const clientHandler = await SocketioClientHandler.create<DemoResource>(
			{
				namespace: '/demo-resource',
				sessionId: 'session-123'
			},
			{
				transferred: (data) => {
					overridesCalled.transferred = data;
				},
				deleted: (id) => {
					overridesCalled.deleted = id;
				},
				status: (status) => {
					overridesCalled.status = status;
				}
			}
		);

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

	// #endregion: Tests for constructor

	// #region: Tests for Event Emitters:

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

	test('submitBulk emits "submit" event with correct payload', async () => {
		testSocketio.pendingTemplate = { name: 'bulk pending' };
		testSocketio.createPending() as DemoResource;
		testSocketio.createPending() as DemoResource;

		testSocketio.submitBulk();

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(2);
			expect(serverMessages).toContainEqual({
				event: 'submit',
				data: [
					expect.objectContaining({ payload: expect.objectContaining({ name: 'bulk pending' }) })
				]
			});
		});
		expect(serverMessages).toContainEqual({
			event: 'submit',
			data: [
				expect.objectContaining({ payload: expect.objectContaining({ name: 'bulk pending' }) })
			]
		});
	});

	test('deleteEntity emits "delete" event with correct payload', async () => {
		testSocketio.deleteEntity('abc');

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'delete',
			data: ['abc']
		});
	});

	test('link emits "link" event with correct payload', async () => {
		testSocketio.link('child-1', 'parent-1', true);

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'link',
			data: [
				expect.objectContaining({
					child_id: 'child-1',
					parent_id: 'parent-1',
					inherit: true
				})
			]
		});
	});

	test('unlink emits "unlink" event with correct payload', async () => {
		testSocketio.unlink('child-1', 'parent-1');

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'unlink',
			data: [
				expect.objectContaining({
					child_id: 'child-1',
					parent_id: 'parent-1'
				})
			]
		});
	});

	test.todo('changeLink emits "change_link" event with correct payload', async () => {
		testSocketio.changeLink('child-1', 'parent-2', false);

		// await vi.waitFor(() => {
		// 	expect(serverMessages.length).toBe(1);
		// });

		// expect(serverMessages).toContainEqual({
		// 	event: 'change_link',
		// 	data: [
		// 		expect.objectContaining({
		// 			childId: 'child-1',
		// 			parentId: 'parent-2',
		// 			inherit: false
		// 		})
		// 	]
		// });
	});

	test.todo('move emits "move" event with correct payload', async () => {
		testSocketio.move('child-1', 'before', 'parent-1', 'other-child');

		// await vi.waitFor(() => {
		// 	expect(serverMessages.length).toBe(1);
		// });

		// expect(serverMessages).toContainEqual({
		// 	event: 'move',
		// 	data: [
		// 		expect.objectContaining({
		// 			childId: 'child-1',
		// 			position: 'before',
		// 			parentId: 'parent-1',
		// 			otherChildId: 'other-child'
		// 		})
		// 	]
		// });
	});

	test('shareEntity emits "share" event with correct payload', async () => {
		const accessPolicy = { resource_id: 'resource-1', identity_id: 'identity-1' } as AccessPolicy;
		testSocketio.shareEntity(accessPolicy);

		await vi.waitFor(() => {
			expect(serverMessages.length).toBe(1);
		});

		expect(serverMessages).toContainEqual({
			event: 'share',
			data: [
				expect.objectContaining({
					resource_id: 'resource-1',
					identity_id: 'identity-1'
				})
			]
		});
	});
	// #endregion: Tests for Event Emitters

	// #region Tests for Event Handlers:

	test('handleTransferred adds entity in state', async () => {
		const transferredEntity = { id: 'srv-1', name: 'from server' } as DemoResource;
		testSocketio.handleTransferred(transferredEntity);

		await vi.waitFor(() => {
			expect(testSocketio.entities.map((e) => e.id)).toContain('srv-1');
			expect(testSocketio.entities.map((e) => e.name)).toContain('from server');
		});
	});

	test('handleTransferred updates existing entity in state', async () => {
		const initialEntity = { id: 'srv-1', name: 'initial' } as DemoResource;
		testSocketio.entities = [initialEntity];

		const updatedEntity = { id: 'srv-1', name: 'updated from server' } as DemoResource;
		testSocketio.handleTransferred(updatedEntity);
		await vi.waitFor(() => {
			expect(testSocketio.entities.length).toBe(1);
			expect(testSocketio.entities[0].id).toBe('srv-1');
			expect(testSocketio.entities[0].name).toBe('updated from server');
		});
	});

	test('handleDeleted removes entity from state', async () => {
		const entityToDelete = { id: 'srv-1', name: 'to be deleted' } as DemoResource;
		testSocketio.entities = [entityToDelete];

		testSocketio.handleDeleted('srv-1');
		await vi.waitFor(() => {
			expect(testSocketio.entities.map((e) => e.id)).not.toContain('srv-1');
		});
	});

	test('handleStatus for "success:created" replaces submitted_id with id and removes pending entity', async () => {
		testSocketio.pendingEntities = [{ id: 'pending-1', name: 'pending' } as DemoResource];

		serverSocket.emit('status', { success: 'created', id: 'srv-1', submitted_id: 'pending-1' });

		await vi.waitFor(() => {
			expect(testSocketio.entities.length).toBe(1);
			expect(testSocketio.entities).toEqual([{ id: 'srv-1', name: 'pending' }]);
			expect(testSocketio.entities.map((e) => e.id)).not.toContain('submitted-1');
			expect(testSocketio.pendingEntities.map((e) => e.id)).not.toContain('pending-1');
		});
	});

	test('handleStatus for "success:shared" triggers read for the updated entity', async () => {
		serverSocket.emit('status', { success: 'shared', id: 'srv-1' });

		await vi.waitFor(() => {
			expect(serverMessages[0]).toEqual({ event: 'read', data: ['srv-1'] });
		});
	});

	test('handleStatus for "success:unshared" triggers read for the updated entity', async () => {
		serverSocket.emit('status', { success: 'unshared', id: 'srv-1' });

		await vi.waitFor(() => {
			expect(serverMessages[0]).toEqual({ event: 'read', data: ['srv-1'] });
		});
	});

	test('handleStatus for "success:linked" and existing hierarchy updates the hierarchy and does not trigger read for the child entity', async () => {
		testSocketio.hierarchies = {
			'child-1': [
				{ child_id: 'child-1', parent_id: 'parent-from-describe', inherit: false, order: 0 }
			]
		};
		serverSocket.emit('status', {
			success: 'linked',
			id: 'child-1',
			parent_id: 'parent-from-describe',
			inherit: true,
			order: 0
		});

		const emitSpy = vi.spyOn(testSocketio.client, 'emit');

		await vi.waitFor(() => {
			expect(Object.keys(testSocketio.hierarchies).length).toBe(1);
			expect(testSocketio.hierarchies['child-1'].length).toBe(1);
			expect(testSocketio.hierarchies['child-1']).toEqual([
				{ child_id: 'child-1', parent_id: 'parent-from-describe', inherit: true, order: 0 }
			]);
			expect(emitSpy).not.toHaveBeenCalledWith('read', 'child-1');
		});
	});

	test('handleStatus for "success:linked" and no existing hierarchy adds the hierarchy and triggers read for the child entity', async () => {
		serverSocket.emit('status', {
			success: 'linked',
			id: 'child-1',
			parent_id: 'parent-from-describe',
			inherit: true
		});

		await vi.waitFor(() => {
			expect(testSocketio.hierarchies['child-1']).toEqual([
				{ child_id: 'child-1', parent_id: 'parent-from-describe', inherit: true, order: undefined }
			]);
			expect(serverMessages.length).toBe(1);
			expect(serverMessages[0]).toEqual({ event: 'read', data: ['child-1'] });
		});
	});

	test('handleStatus for "success:linked" from another parent, than the classes parent-id does not get added to hierarchies', async () => {
		serverSocket.emit('status', {
			success: 'linked',
			id: 'child-1',
			parent_id: 'other-parent',
			inherit: true,
			order: 0
		});

		const emitSpy = vi.spyOn(testSocketio.client, 'emit');

		await vi.waitFor(() => {
			expect(Object.keys(testSocketio.hierarchies).length).toBe(0);
			expect(emitSpy).not.toHaveBeenCalledWith('read', 'child-1');
		});
	});

	test('handleStatus for "success:unlinked" removes the hierarchy and triggers read for the child entity', async () => {
		testSocketio.hierarchies = {
			'child-1': [{ child_id: 'child-1', parent_id: 'parent-from-describe', inherit: true }]
		};

		serverSocket.emit('status', {
			success: 'unlinked',
			id: 'child-1',
			parent_id: 'parent-from-describe'
		});

		const emitSpy = vi.spyOn(testSocketio.client, 'emit');

		await vi.waitFor(() => {
			expect(testSocketio.hierarchies['child-1']).toEqual([]);
			expect(serverMessages.length).toBe(0);
			expect(emitSpy).not.toHaveBeenCalledWith('read', 'child-1');
		});
	});

	test.todo('handleStatus for "error" logs the error message', async () => {
		const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

		serverSocket.emit('status', { error: 'Something went wrong' });

		await vi.waitFor(() => {
			expect(consoleErrorSpy).toHaveBeenCalledWith(
				'🧦🔥 SocketIO error status received:',
				'Something went wrong'
			);
		});

		consoleErrorSpy.mockRestore();
	});
});
