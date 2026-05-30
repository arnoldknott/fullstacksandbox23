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

		rendered.view.link('child-8', { inherit: false });

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

	it('unlink emits a hierarchy and eagerly drops the child from linked', async () => {
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
		expect(rendered.view.linked.map((g) => g.id)).toEqual(['g-2']);
	});

	it('delete delegates to socketio.deleteEntity for server-side ids', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			initial: () => [createGroup({ id: 'g-1' })]
		});
		await tick();

		rendered.view.delete('g-1');

		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('delete', 'g-1');
	});

	it('submit registers the entity as pending, emits submit, and returns the preliminary id', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			defaultInherit: false
		});
		await tick();

		const draft = createGroup({ id: '', name: 'fresh' });
		const preliminaryId = rendered.view.submit(draft);

		expect(preliminaryId).toMatch(/^new_/);
		expect(rendered.view.pending).toHaveLength(1);
		expect(rendered.view.pending[0]?.id).toBe(preliminaryId);
		expect(socketIoClient.socket.emit).toHaveBeenCalledWith('submit', {
			payload: { ...draft, id: preliminaryId },
			parent_id: 'parent-1'
		});
	});

	it('submit reuses an existing new_* id without generating a fresh one', async () => {
		const rendered = renderGroupRelation({ parent: () => parentUeberGroup });
		await tick();

		const draft = createGroup({ id: 'new_abc123', name: 'preset' });
		const preliminaryId = rendered.view.submit(draft);

		expect(preliminaryId).toBe('new_abc123');
		expect(rendered.view.pending[0]?.entity.id).toBe('new_abc123');
	});

	it('submitBulk in suffixes mode clones template and submits each entry', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			defaultInherit: true
		});
		await tick();

		const template = createGroup({ id: '', name: 'team' });
		const ids = rendered.view.submitBulk(template, { suffixes: ['_1', '_2'] });

		expect(ids).toHaveLength(2);
		expect(rendered.view.pending.map((p) => p.entity.name)).toEqual(['team_1', 'team_2']);
		const submitCalls = socketIoClient.socket.emit.mock.calls.filter(
			([event]) => event === 'submit'
		);
		expect(submitCalls).toHaveLength(2);
		expect(submitCalls[0][1]).toMatchObject({
			payload: { name: 'team_1' },
			parent_id: 'parent-1',
			inherit: true
		});
	});

	it('submitBulk in entries mode submits each entry as-is', async () => {
		const rendered = renderGroupRelation({ parent: () => parentUeberGroup });
		await tick();

		const entries = [createGroup({ id: '', name: 'alpha' }), createGroup({ id: '', name: 'beta' })];
		const ids = rendered.view.submitBulk(createGroup({ id: '', name: 'unused' }), { entries });

		expect(ids).toHaveLength(2);
		expect(rendered.view.pending.map((p) => p.entity.name)).toEqual(['alpha', 'beta']);
	});

	it('reseed replaces linked with the given snapshot', async () => {
		const rendered = renderGroupRelation({
			parent: () => parentUeberGroup,
			initial: () => [createGroup({ id: 'g-1' })]
		});
		await tick();

		rendered.view.reseed([createGroup({ id: 'g-99' })]);
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
		it('status:created promotes a pending entry into linked with the server id', async () => {
			const rendered = renderGroupRelation({ parent: () => parentUeberGroup });
			await tick();

			const preliminaryId = rendered.view.submit(createGroup({ id: '', name: 'fresh' }));
			socketIoClient.trigger('status', {
				success: 'created',
				id: 'server-1',
				submitted_id: preliminaryId
			});

			expect(rendered.view.pending).toEqual([]);
			expect(rendered.view.linked.map((g) => g.id)).toEqual(['server-1']);
			expect(rendered.view.linked[0]?.name).toBe('fresh');
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

		it('status:linked (matching parent) moves an entity from socketio.entities to linked', async () => {
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
			expect(rendered.socketio.entities.map((g) => g.id)).toEqual([]);
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

		it('status:unlinked (matching parent) moves an entity from linked back to socketio.entities', async () => {
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

			expect(rendered.view.linked.find((g) => g.id === 'g-1')?.name).toBe('after');
		});

		it('deleted removes from both linked and pending', async () => {
			const rendered = renderGroupRelation({
				parent: () => parentUeberGroup,
				initial: () => [createGroup({ id: 'g-1' })]
			});
			await tick();
			const preliminaryId = rendered.view.submit(createGroup({ id: '', name: 'pending' }));

			socketIoClient.trigger('deleted', 'g-1');
			socketIoClient.trigger('deleted', preliminaryId);

			expect(rendered.view.linked).toEqual([]);
			expect(rendered.view.pending).toEqual([]);
		});
	});

	describe('getId override', () => {
		it('uses a custom id extractor for all lookups', async () => {
			type CustomKeyed = GroupExtended & { external_id: string };
			const make = (external: string, base: Partial<GroupExtended> = {}) =>
				({ ...createGroup({ id: '_ignored', ...base }), external_id: external }) as CustomKeyed;

			const rendered = renderRelationHandler<UeberGroupExtended, CustomKeyed>({
				parent: () => parentUeberGroup,
				initial: () => [make('ext-1', { name: 'one' })],
				entities: [make('ext-1'), make('ext-2', { name: 'two' })],
				getId: (child) => child.external_id
			});
			await tick();

			expect(rendered.view.linked.map((g) => g.external_id)).toEqual(['ext-1']);
			expect(rendered.view.unlinked.map((g) => g.external_id)).toEqual(['ext-2']);

			rendered.view.unlink('ext-1');
			expect(rendered.view.linked).toEqual([]);
		});
	});
});
