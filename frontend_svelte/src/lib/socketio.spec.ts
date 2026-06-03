import { tick } from 'svelte';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { Action } from '$lib/accessHandler';
import type { SocketioStatus } from '$lib/socketio.svelte';
import type { DemoResourceExtended } from '$lib/types.d.ts';

import { createDemoResource } from '../test/factories/entities';
import { renderSocketIO, type RenderSocketIOOptions } from '../test/renderSocketIO';

const renderDemoSocketIO = (options: RenderSocketIOOptions<DemoResourceExtended> = {}) =>
	renderSocketIO<DemoResourceExtended>(options);

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

beforeEach(() => {
	socketIoClient.reset();
});

describe('SocketIO', () => {
	it('connects with localhost http URL and registers the three default listeners', () => {
		renderDemoSocketIO({
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
		renderDemoSocketIO({
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
		renderDemoSocketIO({
			defaultHandlers: { transferred: false, status: false }
		});

		expect(socketIoClient.socket.on.mock.calls.map(([event]) => event)).toEqual(['deleted']);
	});

	it('seeds entities from props and mirrors reactive updates; null preserves current entities', async () => {
		const initial = [createDemoResource({ id: 'first' })];
		const next = [createDemoResource({ id: 'second' }), createDemoResource({ id: 'third' })];

		const rendered = renderDemoSocketIO({ entities: initial });
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

	it('handleTransferred updates existing or prepends new, handleDeleted removes by id', async () => {
		const rendered = renderDemoSocketIO({
			entities: [createDemoResource({ id: 'kept', name: 'before' })]
		});
		await tick();

		rendered.instance.handleTransferred(createDemoResource({ id: 'kept', name: 'after' }));
		expect(rendered.instance.entities.find((entity) => entity.id === 'kept')?.name).toBe('after');

		rendered.instance.handleTransferred(createDemoResource({ id: 'incoming' }));
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['incoming', 'kept']);

		rendered.instance.handleDeleted('kept');
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['incoming']);
	});

	it('submitEntity emits without optional flags when none are passed (explicit entity, no refill)', () => {
		const rendered = renderDemoSocketIO();
		const payload = createDemoResource({ id: 'plain' });

		rendered.instance.submitEntity(payload);

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('submit', { payload });
	});

	it('submitEntity() no-arg submits first pending and auto-refills pendingEntities', () => {
		const rendered = renderDemoSocketIO();
		const pending = rendered.instance.createPending();
		const pendingId = pending.id;

		rendered.instance.submitEntity();

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('submit', { payload: pending });
		// Submitted drafts remain pending until backend confirms `created`, so refill adds one more.
		expect(rendered.instance.pendingEntities).toHaveLength(2);
		expect(rendered.instance.pendingEntities[0].id).not.toBe(pendingId);
		expect(rendered.instance.pendingEntities[1].id).toBe(pendingId);
	});

	it('submitEntity() no-arg is a no-op when there are no pending entities', () => {
		const rendered = renderDemoSocketIO();

		rendered.instance.submitEntity();

		expect(socketIoClient.socket.emit).not.toHaveBeenCalledWith('submit', expect.anything());
	});

	it('submitEntity with explicit entity keeps pending drafts unchanged until backend confirms', () => {
		const rendered = renderDemoSocketIO();
		const pending = rendered.instance.createPending();

		rendered.instance.submitEntity(pending);

		expect(rendered.instance.pendingEntities).toEqual([pending]);
		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('submit', { payload: pending });
	});

	it('submitEntity emits parent_id / inherit / public / public_action when provided', () => {
		const rendered = renderDemoSocketIO();
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

	it('submitBulk emits all pending entities with shared options', () => {
		const rendered = renderDemoSocketIO();
		const p1 = rendered.instance.createPending({ name: 'first' } as never);
		const p2 = rendered.instance.createPending({ name: 'second' } as never);

		rendered.instance.submitBulk('parent-bulk', true);

		const emits = socketIoClient.socket.emit.mock.calls.filter(([event]) => event === 'submit');
		expect(emits).toHaveLength(2);
		expect(emits[0][1]).toMatchObject({ payload: p2, parent_id: 'parent-bulk', inherit: true });
		expect(emits[1][1]).toMatchObject({ payload: p1, parent_id: 'parent-bulk', inherit: true });
		// pending list is not auto-refilled after submitBulk
		expect(rendered.instance.pendingEntities).toHaveLength(2);
	});

	it('submitBulk is a no-op when there are no pending entities', () => {
		const rendered = renderDemoSocketIO();

		rendered.instance.submitBulk();

		expect(socketIoClient.socket.emit).not.toHaveBeenCalledWith('submit', expect.anything());
	});

	it('deleteEntity removes new_* ids from pendingEntities without emitting delete', async () => {
		const rendered = renderDemoSocketIO();
		const firstPending = rendered.instance.createPending({ name: 'first' } as never);
		const secondPending = rendered.instance.createPending({ name: 'second' } as never);
		await tick();

		rendered.instance.deleteEntity(firstPending.id);

		expect(rendered.instance.pendingEntities.map((entity) => entity.id)).toEqual([
			secondPending.id
		]);
		expect(rendered.instance.entities).toEqual([]);
		expect(socketIoClient.socket.emit).not.toHaveBeenCalledWith('delete', firstPending.id);
	});

	it('deleteEntity emits delete for server-side ids', async () => {
		const rendered = renderDemoSocketIO({
			entities: [createDemoResource({ id: 'server-1' })]
		});
		await tick();

		rendered.instance.deleteEntity('server-1');

		expect(socketIoClient.socket.emit).toHaveBeenLastCalledWith('delete', 'server-1');
		expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['server-1']);
	});

	it('shareEntity emits "share" with the access policy', () => {
		const rendered = renderDemoSocketIO();
		const accessPolicy = {
			resource_id: 'res-1',
			identity_id: 'user-1',
			action: Action.READ
		};

		rendered.instance.shareEntity(accessPolicy);

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('share', accessPolicy);
	});

	it('handleStatus moves pending to entities with server id on created, and re-reads on shared/unshared', async () => {
		const rendered = renderDemoSocketIO();
		const pending = rendered.instance.createPending();
		await tick();

		rendered.instance.handleStatus({
			success: 'created',
			id: 'server-42',
			submitted_id: pending.id
		});
		expect(rendered.instance.pendingEntities).toEqual([]);
		expect(rendered.instance.entities).toHaveLength(1);
		expect(rendered.instance.entities[0]?.id).toBe('server-42');

		rendered.instance.handleStatus({ success: 'shared', id: 'server-42' });
		rendered.instance.handleStatus({ success: 'unshared', id: 'server-42' });

		const readEmits = socketIoClient.socket.emit.mock.calls.filter(([event]) => event === 'read');
		expect(readEmits).toEqual([
			['read', 'server-42'],
			['read', 'server-42']
		]);
	});

	it('handleStatus is a no-op for updated / deleted / linked / unlinked / error branches', () => {
		const rendered = renderDemoSocketIO({
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

	describe('createPending', () => {
		it('without a template or overrides returns an entity with only a fresh new_* id', () => {
			const rendered = renderDemoSocketIO();
			const first = rendered.instance.createPending();
			const second = rendered.instance.createPending();

			expect(first.id).toMatch(/^new_[a-z0-9]+$/);
			expect(Object.keys(first)).toEqual(['id']);
			expect(first.id).not.toBe(second.id);
			expect(rendered.instance.pendingEntities).toHaveLength(2);
			expect(rendered.instance.pendingEntities[0]).toMatchObject({ id: second.id });
			expect(rendered.instance.pendingEntities[1]).toMatchObject({ id: first.id });
			// Does not touch the managed entities array.
			expect(rendered.instance.entities).toEqual([]);
		});

		it('merges the configured template with a fresh id on every call', () => {
			const rendered = renderDemoSocketIO({
				pendingTemplate: () => ({ name: '', description: '' })
			});

			const pending = rendered.instance.createPending();

			expect(pending).toMatchObject({ name: '', description: '' });
			expect(pending.id).toMatch(/^new_[a-z0-9]+$/);
			expect(rendered.instance.pendingEntities).toHaveLength(1);
		});

		it('re-evaluates the template thunk on each call', () => {
			let counter = 0;
			const rendered = renderDemoSocketIO({
				pendingTemplate: () => ({ name: `draft-${++counter}` })
			});

			expect(rendered.instance.createPending()).toMatchObject({ name: 'draft-1' });
			expect(rendered.instance.createPending()).toMatchObject({ name: 'draft-2' });
			expect(rendered.instance.pendingEntities).toHaveLength(2);
		});

		it('overrides win over the template, and the generated id always wins over both', () => {
			const rendered = renderDemoSocketIO({
				pendingTemplate: () => ({ name: 'from-template', description: 'tpl' })
			});

			const pending = rendered.instance.createPending({
				id: 'caller-supplied-id',
				name: 'from-override'
			} as Partial<DemoResourceExtended>);

			expect(pending.name).toBe('from-override');
			expect(pending.description).toBe('tpl');
			expect(pending.id).not.toBe('caller-supplied-id');
			expect(pending.id).toMatch(/^new_[a-z0-9]+$/);
			expect(rendered.instance.pendingEntities[0]).toMatchObject({
				id: pending.id,
				name: 'from-override',
				description: 'tpl'
			});
		});
	});

	describe('listener wiring (server-emitted events)', () => {
		it('routes inbound `transferred` events into entity state', async () => {
			const rendered = renderDemoSocketIO({
				entities: [createDemoResource({ id: 'existing', name: 'before' })]
			});
			await tick();

			socketIoClient.trigger('transferred', createDemoResource({ id: 'existing', name: 'after' }));
			expect(rendered.instance.entities.find((entity) => entity.id === 'existing')?.name).toBe(
				'after'
			);

			socketIoClient.trigger('transferred', createDemoResource({ id: 'fresh' }));
			expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['fresh', 'existing']);
		});

		it('routes inbound `deleted` events into entity state', async () => {
			const rendered = renderDemoSocketIO({
				entities: [createDemoResource({ id: 'a' }), createDemoResource({ id: 'b' })]
			});
			await tick();

			socketIoClient.trigger('deleted', 'a');
			expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['b']);
		});

		it('routes inbound `status` events: created moves pending to entities; shared/unshared re-read', async () => {
			const rendered = renderDemoSocketIO();
			const pending = rendered.instance.createPending();
			await tick();

			socketIoClient.trigger('status', {
				success: 'created',
				id: 'server-77',
				submitted_id: pending.id
			});
			expect(rendered.instance.entities[0]?.id).toBe('server-77');
			expect(rendered.instance.pendingEntities).toHaveLength(0);

			socketIoClient.trigger('status', { success: 'shared', id: 'server-77' });
			socketIoClient.trigger('status', { success: 'unshared', id: 'server-77' });
			const readEmits = socketIoClient.socket.emit.mock.calls.filter(([event]) => event === 'read');
			expect(readEmits).toEqual([
				['read', 'server-77'],
				['read', 'server-77']
			]);
		});

		it('does not route events for opted-out default handlers', async () => {
			const rendered = renderDemoSocketIO({
				entities: [createDemoResource({ id: 'survives' })],
				defaultHandlers: { deleted: false }
			});
			await tick();

			// No `deleted` listener was registered, so the trigger is a no-op.
			socketIoClient.trigger('deleted', 'survives');
			expect(rendered.instance.entities.map((entity) => entity.id)).toEqual(['survives']);
		});
	});
});
