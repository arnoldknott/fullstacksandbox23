import { tick } from 'svelte';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { GroupExtended, UeberGroupExtended } from '$lib/types.d.ts';

import { createGroup, createUeberGroup } from '../test/factories/entities';
import {
	renderRelationHandler,
	type RenderRelationHandlerOptions
} from '../test/renderRelationHandler';

const renderGroupRelation = (
	options: RenderRelationHandlerOptions<UeberGroupExtended, GroupExtended> = {}
) => renderRelationHandler<UeberGroupExtended, GroupExtended>(options);

// Mirror of `socketio.spec.ts`'s hoisted mock. See that file for the rationale
// behind inlining instead of importing `mocks/socketIoClient.ts`.
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

const parentUeberGroup = createUeberGroup({ id: 'parent-1' });

describe('RelationHandler', () => {
	it('seeds linked from the initial thunk and reseeds when its reactive source changes', async () => {
		const first = [createGroup({ id: 'g-1' })];
		const second = [createGroup({ id: 'g-2' }), createGroup({ id: 'g-3' })];

		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			initial: () => first
		});
		await tick();

		expect(rendered.view.linked.map((g) => g.id)).toEqual(['g-1']);

		await rendered.rerender({
			parent: () => parentUeberGroup,
			initial: () => second,
			onInstance: () => {}
		});
		await tick();

		expect(rendered.view.linked.map((g) => g.id)).toEqual(['g-2', 'g-3']);
	});

	it('exposes unlinked as socketio.entities minus linked', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			initial: () => [createGroup({ id: 'linked-1' })],
			entities: [createGroup({ id: 'linked-1' }), createGroup({ id: 'free-1' })]
		});
		await tick();

		expect(rendered.view.linked.map((g) => g.id)).toEqual(['linked-1']);
		expect(rendered.view.unlinked.map((g) => g.id)).toEqual(['free-1']);
	});

	it('link emits a hierarchy with the parent id and the default inherit flag', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			defaultInherit: true
		});
		await tick();

		rendered.view.link('child-7');

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('link', {
			child_id: 'child-7',
			parent_id: 'parent-1',
			inherit: true
		});
	});

	it('link honors a per-call inherit override', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			defaultInherit: true
		});
		await tick();

		rendered.view.link('child-8', false);

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('link', {
			child_id: 'child-8',
			parent_id: 'parent-1',
			inherit: false
		});
	});

	it('link is a no-op when the parent thunk yields undefined', async () => {
		const rendered = renderGroupRelation({ parent: () => undefined });
		await tick();

		rendered.view.link('child-9');

		expect(socketIoClient.socket.emit).not.toHaveBeenCalledWith('link', expect.anything());
	});

	it('unlink emits a hierarchy and waits for status:unlinked before dropping linked', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			initial: () => [createGroup({ id: 'g-1' }), createGroup({ id: 'g-2' })]
		});
		await tick();

		rendered.view.unlink('g-1');

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('unlink', {
			child_id: 'g-1',
			parent_id: 'parent-1'
		});
		expect(rendered.view.linked.map((g) => g.id)).toEqual(['g-1', 'g-2']);
	});

	it('getChild returns the registered relation and addChild throws on duplicate keys', async () => {
		const rendered = renderGroupRelation({ parent: () => parentUeberGroup });
		await tick();

		expect(rendered.relationHandler.getChild('children')).toBe(rendered.view);
		expect(() => rendered.relationHandler.addChild('children', rendered.socketio)).toThrow(
			'Child with key "children" already exists.'
		);
	});

	it('pending mirrors socketio.pendingEntities (creation is owned by SocketIO)', async () => {
		const rendered = renderGroupRelation({ parent: () => parentUeberGroup });
		await tick();

		const firstPending = rendered.socketio.createPending(createGroup({ id: '', name: 'alpha' }));
		const secondPending = rendered.socketio.createPending(createGroup({ id: '', name: 'beta' }));

		expect(rendered.view.pending.map((p) => (p as GroupExtended).id)).toEqual([
			secondPending.id,
			firstPending.id
		]);
		expect(rendered.view.pending.map((p) => (p as GroupExtended).name)).toEqual(['beta', 'alpha']);
	});

	it('reseed replaces linked with the given snapshot', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			initial: () => [createGroup({ id: 'g-1' })]
		});
		await tick();

		// `linked` is derived from `socketio.entities`; mirror a real page by
		// putting the entity into the SocketIO store before reseeding.
		const g99 = createGroup({ id: 'g-99' });
		rendered.socketio.entities = [...rendered.socketio.entities, g99];
		rendered.view.reseed([g99]);
		expect(rendered.view.linked.map((g) => g.id)).toEqual(['g-99']);

		rendered.view.reseed(null);
		expect(rendered.view.linked).toEqual([]);
	});

	it('move is a no-op stub (reordering is pending backend support)', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			initial: () => [createGroup({ id: 'g-1' }), createGroup({ id: 'g-2' })]
		});
		await tick();

		const before = rendered.view.linked.map((g) => g.id);
		rendered.view.move('g-1', 1);
		expect(rendered.view.linked.map((g) => g.id)).toEqual(before);
	});

	describe('inbound status events', () => {
		it('status:created clears pending and updates local entity id; status:linked adds hierarchy', async () => {
			const rendered = renderGroupRelation({ parent: () => parentUeberGroup });
			await tick();

			const pending = rendered.socketio.createPending(createGroup({ id: '', name: 'fresh' }));
			socketIoClient.trigger('status', {
				success: 'created',
				id: 'server-1',
				submitted_id: pending.id
			});

			expect(rendered.view.pending).toEqual([]);
			expect(rendered.socketio.entities.map((g) => g.id)).toEqual(['server-1']);
			expect(rendered.view.linked).toEqual([]);

			socketIoClient.trigger('status', {
				success: 'linked',
				id: 'server-1',
				parent_id: 'parent-1',
				inherit: true
			});

			expect(rendered.view.linked.map((g) => g.id)).toEqual(['server-1']);
			expect((rendered.view.linked[0] as GroupExtended | undefined)?.name).toBe('fresh');
		});

		it('status:created without a matching pending entry is ignored', async () => {
			const rendered = renderGroupRelation({ parent: () => parentUeberGroup });
			await tick();

			socketIoClient.trigger('status', {
				success: 'created',
				id: 'server-x',
				submitted_id: 'new_unknown'
			});

			expect(rendered.view.linked).toEqual([]);
		});

		it('status:linked (matching parent) adds the entity to linked (entities are the source of truth)', async () => {
			const rendered = renderGroupRelation({
				parent: () => parentUeberGroup,
				entities: [createGroup({ id: 'free-1', name: 'free' })]
			});
			await tick();

			socketIoClient.trigger('status', {
				success: 'linked',
				id: 'free-1',
				parent_id: 'parent-1',
				inherit: true
			});

			expect(rendered.view.linked.map((g) => g.id)).toEqual(['free-1']);
			// Entity stays in socketio.entities; `unlinked` is the derived complement.
			expect(rendered.socketio.entities.map((g) => g.id)).toEqual(['free-1']);
			expect(rendered.view.unlinked).toEqual([]);
		});

		it('status:linked for a different parent is ignored', async () => {
			const rendered = renderGroupRelation({
				parent: () => parentUeberGroup,
				entities: [createGroup({ id: 'free-1' })]
			});
			await tick();

			socketIoClient.trigger('status', {
				success: 'linked',
				id: 'free-1',
				parent_id: 'other-parent',
				inherit: true
			});

			expect(rendered.view.linked).toEqual([]);
			expect(rendered.socketio.entities.map((g) => g.id)).toEqual(['free-1']);
		});

		it('status:unlinked (matching parent) drops the entity from linked while keeping it in entities', async () => {
			const rendered = renderGroupRelation({
				parent: () => parentUeberGroup,
				initial: () => [createGroup({ id: 'g-1' })]
			});
			await tick();

			socketIoClient.trigger('status', {
				success: 'unlinked',
				id: 'g-1',
				parent_id: 'parent-1'
			});

			expect(rendered.view.linked).toEqual([]);
			expect(rendered.socketio.entities.map((g) => g.id)).toEqual(['g-1']);
			expect(rendered.view.unlinked.map((g) => g.id)).toEqual(['g-1']);
		});

		it('status:unlinked for a different parent is ignored', async () => {
			const rendered = renderGroupRelation({
				parent: () => parentUeberGroup,
				initial: () => [createGroup({ id: 'g-1' })]
			});
			await tick();

			socketIoClient.trigger('status', {
				success: 'unlinked',
				id: 'g-1',
				parent_id: 'other-parent'
			});

			expect(rendered.view.linked.map((g) => g.id)).toEqual(['g-1']);
		});
	});

	describe('inbound transferred / deleted events', () => {
		it('transferred patches a matching entry in linked', async () => {
			const rendered = renderGroupRelation({
				parent: () => parentUeberGroup,
				initial: () => [createGroup({ id: 'g-1', name: 'before' })]
			});
			await tick();

			socketIoClient.trigger('transferred', createGroup({ id: 'g-1', name: 'after' }));

			expect(
				(rendered.view.linked.find((g) => g.id === 'g-1') as GroupExtended | undefined)?.name
			).toBe('after');
		});

		it('deleted removes linked hierarchy entries but does not clear pending drafts', async () => {
			const rendered = renderGroupRelation({
				parent: () => parentUeberGroup,
				initial: () => [createGroup({ id: 'g-1' })]
			});
			await tick();
			const pending = rendered.socketio.createPending(createGroup({ id: '', name: 'pending' }));

			socketIoClient.trigger('deleted', 'g-1');
			socketIoClient.trigger('deleted', pending.id);

			expect(rendered.view.linked).toEqual([]);
			expect(rendered.view.pending.map((entry) => entry.id)).toEqual([pending.id]);
		});
	});
});
