import { beforeEach, describe, expect, it, vi } from 'vitest';
import { tick } from 'svelte';
import { Action } from '$lib/accessHandler';
import type { SocketioStatus } from '$lib/socketio.svelte';
import { createDemoResource } from '../test/factories/entities';
import { renderSocketIO } from '../test/renderSocketIO';

// `vi.mock` is hoisted to the top of the file by Vitest, so the mock state it
// references must also be defined before normal module evaluation. `vi.hoisted`
// is the supported escape hatch. We inline the state here instead of importing
// the `mocks/socketIoClient.ts` helper because hoisted code runs before imports
// resolve. The helper remains available for tests that mock at runtime instead
// of via `vi.mock`.
const socketIoClient = vi.hoisted(() => {
	const socket = {
		on: vi.fn(),
		emit: vi.fn(),
		connect: vi.fn(),
		disconnect: vi.fn()
	};
	const io = vi.fn(() => socket);
	return {
		socket,
		io,
		reset: () => {
			socket.on.mockReset();
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

beforeEach(() => {
	socketIoClient.reset();
});

describe('SocketIO', () => {
	it('connects with localhost http URL and registers the three default listeners', () => {
		renderSocketIO({
			connection: {
				namespace: '/demo-resource',
				cookie_session_id: 'session-123',
				query_params: { preview: true, page: 2 }
			}
		});

		expect(socketIoClient.io).toHaveBeenCalledWith('http://localhost:8000/demo-resource', {
			path: '/socketio/v1',
			auth: { 'session-id': 'session-123' },
			query: { preview: true, page: 2 },
			forceNew: true
		});
		expect(socketIoClient.socket.on.mock.calls.map(([event]) => event)).toEqual([
			'transferred',
			'deleted',
			'status'
		]);
		expect(socketIoClient.socket.connect).toHaveBeenCalledTimes(1);
	});

	it('builds an https URL when backendFqdn is not localhost', () => {
		renderSocketIO({
			backendAPIConfiguration: {
				backendFqdn: 'api.example.com',
				restApiPath: '/api/v1',
				websocketPath: '/ws/v1',
				socketIOPath: '/socketio/v1'
			},
			connection: { namespace: '/foo' }
		});

		expect(socketIoClient.io).toHaveBeenCalledWith(
			'https://api.example.com/foo',
			expect.any(Object)
		);
	});

	it('honors defaultHandlers opt-outs', () => {
		renderSocketIO({
			defaultHandlers: { transferred: false, status: false }
		});

		expect(socketIoClient.socket.on.mock.calls.map(([event]) => event)).toEqual(['deleted']);
	});

	it('seeds entities from props and mirrors reactive updates; null preserves current entities', async () => {
		const initial = [createDemoResource({ id: 'first' })];
		const next = [createDemoResource({ id: 'second' }), createDemoResource({ id: 'third' })];

		const rendered = renderSocketIO({ entities: initial });
		await tick();
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['first']);

		await rendered.rerender({ entities: next });
		await tick();
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['second', 'third']);

		await rendered.rerender({ entities: null });
		await tick();
		// null/undefined from the thunk is a no-op: previous entities remain.
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['second', 'third']);
	});

	it('addEntity prepends, handleTransferred updates in place or prepends, handleDeleted removes by id', async () => {
		const rendered = renderSocketIO({
			entities: [createDemoResource({ id: 'kept', name: 'before' })]
		});
		await tick();

		rendered.instance.addEntity(createDemoResource({ id: 'draft', name: 'draft' }));
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['draft', 'kept']);

		rendered.instance.handleTransferred(createDemoResource({ id: 'kept', name: 'after' }));
		expect(rendered.instance.entities.find((entity) => entity.id === 'kept')?.name).toBe('after');

		rendered.instance.handleTransferred(createDemoResource({ id: 'incoming' }));
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual([
			'incoming',
			'draft',
			'kept'
		]);

		rendered.instance.handleDeleted('draft');
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['incoming', 'kept']);
	});

	it('submitEntity emits without optional flags when none are passed', () => {
		const rendered = renderSocketIO();
		const payload = createDemoResource({ id: 'plain' });

		rendered.instance.submitEntity(payload);

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('submit', { payload });
	});

	it('submitEntity emits parent_id / inherit / public / public_action when provided', () => {
		const rendered = renderSocketIO();
		const payload = createDemoResource({ id: 'with-options' });

		rendered.instance.submitEntity(payload, 'parent-1', true, true, Action.READ);

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('submit', {
			payload,
			parent_id: 'parent-1',
			inherit: true,
			public: true,
			public_action: Action.READ
		});
	});

	it('deleteEntity removes new_* ids locally and emits delete for server-side ids', async () => {
		const rendered = renderSocketIO({
			entities: [createDemoResource({ id: 'new_draft' }), createDemoResource({ id: 'server-1' })]
		});
		await tick();

		rendered.instance.deleteEntity('new_draft');
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['server-1']);
		expect(socketIoClient.socket.emit).not.toHaveBeenCalledWith('delete', 'new_draft');

		rendered.instance.deleteEntity('server-1');
		expect(socketIoClient.socket.emit).toHaveBeenLastCalledWith('delete', 'server-1');
	});

	it('handleStatus swaps created submitted_id in place and re-reads on shared/unshared', async () => {
		const rendered = renderSocketIO({
			entities: [createDemoResource({ id: 'new_42', name: 'draft' })]
		});
		await tick();

		rendered.instance.handleStatus({
			success: 'created',
			id: 'server-42',
			submitted_id: 'new_42'
		});
		expect(rendered.instance.entities[0]?.id).toBe('server-42');
		// Existing object identity is preserved (mutated in place).
		expect(rendered.instance.entities[0]?.name).toBe('draft');

		rendered.instance.handleStatus({ success: 'shared', id: 'server-42' });
		rendered.instance.handleStatus({ success: 'unshared', id: 'server-42' });

		const readEmits = socketIoClient.socket.emit.mock.calls.filter(([event]) => event === 'read');
		expect(readEmits).toEqual([
			['read', 'server-42'],
			['read', 'server-42']
		]);
	});

	it('handleStatus is a no-op for updated / deleted / linked / unlinked / error branches', () => {
		const rendered = renderSocketIO({
			entities: [createDemoResource({ id: 'untouched' })]
		});

		const branches: SocketioStatus[] = [
			{ success: 'updated', id: 'untouched' },
			{ success: 'deleted', id: 'untouched' },
			{ success: 'linked', id: 'a', parent_id: 'b', inherit: false },
			{ success: 'unlinked', id: 'a', parent_id: 'b' },
			{ error: 'boom' }
		];
		for (const status of branches) rendered.instance.handleStatus(status);

		expect(rendered.instance.entities[0]?.id).toBe('untouched');
		expect(socketIoClient.socket.emit).not.toHaveBeenCalledWith('read', expect.anything());
	});
});
