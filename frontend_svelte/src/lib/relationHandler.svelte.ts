import type { SocketIO, SocketioStatus } from '$lib/socketio.svelte';
import type { AnyEntityExtended, Hierarchy } from '$lib/types.d.ts';

/**
 * Reactive surface for one child relation, returned by `RelationHandler.addChild(...)`
 * and retrievable later via `RelationHandler.getChild(key)`.
 *
 * `linked` / `pending` / `unlinked` are derived views that resolve hierarchy
 * `child_id`s against `socketio.entities`. The entity data lives entirely in
 * `SocketIO`; `RelationHandler` only owns the `Hierarchy[]`.
 */
export interface Relation {
	readonly hierarchies: Hierarchy[];
	readonly linked: AnyEntityExtended[];
	readonly pending: AnyEntityExtended[];
	readonly unlinked: AnyEntityExtended[];

	link(childId: string, inherit?: boolean): void;
	unlink(childId: string): void;
	delete(childId: string): void;

	/**
	 * Optimistically add the entity to `socketio.entities` with a fresh `new_*`
	 * id, register the hierarchy, and emit `submit`. Returns the preliminary id;
	 * SocketIO swaps it for the server id on `status:created`, and the
	 * hierarchy's `child_id` follows.
	 */
	submit(entity: AnyEntityExtended, inherit?: boolean): string;

	/**
	 * Either clone `template` for each suffix (appending to `name`), or submit
	 * each fully-formed entry as-is. Returns the preliminary ids in order.
	 */
	submitBulk(
		template: AnyEntityExtended,
		input: { suffixes: string[] } | { entries: AnyEntityExtended[] },
		inherit?: boolean
	): string[];

	/** Replace the hierarchy list from a fresh snapshot (e.g. after route data changes). */
	reseed(next: { id: string }[] | undefined | null): void;

	move(childId: string, toIndex: number): void;
}

class ChildSlot implements Relation {
	#socketio: SocketIO<AnyEntityExtended>;
	#hierarchies = $state<Hierarchy[]>([]);
	#parent: () => { id: string } | undefined;
	#defaultInherit: boolean;

	constructor(
		socketio: SocketIO<AnyEntityExtended>,
		parent: () => { id: string } | undefined,
		initial?: () => { id: string }[] | undefined | null,
		defaultInherit?: boolean
	) {
		this.#socketio = socketio;
		this.#parent = parent;
		this.#defaultInherit = defaultInherit ?? false;

		if (initial) {
			$effect(() => {
				const next = initial!();
				if (next) this.reseed(next);
			});
		}

		this.#socketio.client.on('deleted', (resourceId: string) => {
			this.#hierarchies = this.#hierarchies.filter((h) => h.child_id !== resourceId);
		});

		this.#socketio.client.on('status', (status: SocketioStatus) => {
			if (!('success' in status)) return;
			const parentId = this.#parent()?.id;

			if (status.success === 'created') {
				// SocketIO has already swapped the entity's id in place. Mirror that
				// onto our hierarchy so `linked` keeps resolving correctly.
				this.#hierarchies = this.#hierarchies.map((h) =>
					h.child_id === status.submitted_id ? { ...h, child_id: status.id } : h
				);
			} else if (status.success === 'linked') {
				if (!parentId || status.parent_id !== parentId) return;
				if (!this.#hierarchies.some((h) => h.child_id === status.id)) {
					this.#hierarchies = [
						...this.#hierarchies,
						{ child_id: status.id, parent_id: parentId, inherit: status.inherit }
					];
				}
			} else if (status.success === 'unlinked') {
				if (!parentId || status.parent_id !== parentId) return;
				this.#hierarchies = this.#hierarchies.filter((h) => h.child_id !== status.id);
			}
		});
	}

	get hierarchies(): Hierarchy[] {
		return this.#hierarchies;
	}

	get linked(): AnyEntityExtended[] {
		const entities = this.#socketio.entities;
		return this.#hierarchies
			.map((h) => entities.find((e) => e.id === h.child_id))
			.filter((e): e is AnyEntityExtended => e !== undefined);
	}

	get pending(): AnyEntityExtended[] {
		return this.linked.filter((e) => e.id.startsWith('new_'));
	}

	get unlinked(): AnyEntityExtended[] {
		return this.#socketio.entities.filter(
			(e) => !this.#hierarchies.some((h) => h.child_id === e.id)
		);
	}

	link(childId: string, inherit?: boolean): void {
		const parentId = this.#parent()?.id;
		if (!parentId) return;
		const hierarchy: Hierarchy = {
			child_id: childId,
			parent_id: parentId,
			inherit: inherit ?? this.#defaultInherit
		};
		this.#socketio.client.emit('link', hierarchy);
		// Reconciliation happens in the `status:linked` handler.
	}

	unlink(childId: string): void {
		const parentId = this.#parent()?.id;
		if (!parentId) return;
		this.#socketio.client.emit('unlink', { child_id: childId, parent_id: parentId });
		// Eager drop; `status:unlinked` will confirm.
		this.#hierarchies = this.#hierarchies.filter((h) => h.child_id !== childId);
	}

	delete(childId: string): void {
		this.#socketio.deleteEntity(childId);
	}

	submit(entity: AnyEntityExtended, inherit?: boolean): string {
		const parentId = this.#parent()?.id;
		const preliminaryId = 'new_' + Math.random().toString(36).substring(2, 9);
		const payload = { ...entity, id: preliminaryId };
		this.#socketio.addEntity(payload);
		this.#socketio.submitEntity(payload, parentId, inherit ?? this.#defaultInherit);
		if (parentId) {
			this.#hierarchies = [
				...this.#hierarchies,
				{
					child_id: preliminaryId,
					parent_id: parentId,
					inherit: inherit ?? this.#defaultInherit
				}
			];
		}
		return preliminaryId;
	}

	submitBulk(
		template: AnyEntityExtended,
		input: { suffixes: string[] } | { entries: AnyEntityExtended[] },
		inherit?: boolean
	): string[] {
		const effectiveInherit = inherit ?? this.#defaultInherit;
		if ('suffixes' in input) {
			return input.suffixes.map((suffix) => {
				const entity = {
					...template,
					name: ((template as AnyEntityExtended & { name?: string }).name ?? '') + suffix
				} as AnyEntityExtended;
				return this.submit(entity, effectiveInherit);
			});
		}
		return input.entries.map((entity) => this.submit(entity, effectiveInherit));
	}

	reseed(next: { id: string }[] | undefined | null): void {
		const parentId = this.#parent()?.id;
		this.#hierarchies = (next ?? []).map((entry) => ({
			child_id: entry.id,
			parent_id: parentId ?? '',
			inherit: this.#defaultInherit
		}));
	}

	move(_childId: string, _toIndex: number): void {
		// TBD: wire to SocketIO reorder once the backend emits a `reordered` status.
		// Today this is a no-op; callers can apply an optimistic local reorder if needed.
	}
}

/**
 * Orchestrates parent ↔ children relationships across SocketIO namespaces.
 *
 * Single responsibility: owns `Hierarchy[]` records per child type. Entity
 * data lives entirely in the respective `SocketIO` instance; the
 * `linked` / `pending` / `unlinked` views are derived by resolving hierarchy
 * `child_id`s against `socketio.entities`.
 *
 * Lifecycle: instantiate during component initialization, inside `onMount`,
 * or inside another effect — same constraint as `SocketIO`, because the
 * `initial` thunk is read inside a `$effect`.
 *
 * Parent-side lifecycle (delete-redirect, refreshing parent fields on
 * `transferred`) stays on the page; RelationHandler only touches hierarchies.
 */
export class RelationHandler<TParent extends AnyEntityExtended> {
	#parent: () => TParent | undefined;
	#children: Record<string, ChildSlot>;

	constructor(parent: () => TParent | undefined) {
		this.#parent = parent;
		this.#children = {};
	}

	addChild(
		key: string,
		socketio: SocketIO<AnyEntityExtended>,
		initial?: () => { id: string }[] | undefined | null,
		defaultInherit?: boolean
	): Relation {
		if (this.#children[key]) {
			throw new Error(`Child with key "${key}" already exists.`);
		}
		const newSlot = new ChildSlot(socketio, this.#parent, initial, defaultInherit);
		this.#children[key] = newSlot;
		return newSlot;
	}

	getChild(key: string): Relation {
		const requestedChild = this.#children[key];
		if (!requestedChild) {
			throw new Error(`Child with key "${key}" does not exist.`);
		}
		return requestedChild;
	}

	// TBD: add removeChild(key) method if needed.
	// That doesn't change the data, just removes the relation handling.
}
