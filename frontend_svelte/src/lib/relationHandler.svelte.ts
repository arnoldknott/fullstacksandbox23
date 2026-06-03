import type { SocketIO, SocketioStatus } from '$lib/socketio.svelte';
import type { AnyEntityExtended, Hierarchy } from '$lib/types.d.ts';

/**
 * Reactive surface for one child relation, returned by `RelationHandler.addChild(...)`
 * and retrievable later via `RelationHandler.getChild(key)`.
 *
 * `linked` / `unlinked` are derived views that resolve hierarchy `child_id`s
 * against `socketio.entities`. `pending` mirrors `socketio.pendingEntities`.
 * Entity state lives in `SocketIO`; `RelationHandler` only owns `Hierarchy[]`.
 */
export interface Relation {
	readonly hierarchies: Hierarchy[];
	readonly linked: AnyEntityExtended[];
	readonly pending: AnyEntityExtended[];
	readonly unlinked: AnyEntityExtended[];

	link(childId: string, inherit?: boolean): void;
	unlink(childId: string): void;
	delete(childId: string): void;

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

			if (status.success === 'linked') {
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
		return this.#socketio.pendingEntities;
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
	}

	delete(childId: string): void {
		this.#socketio.deleteEntity(childId);
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
