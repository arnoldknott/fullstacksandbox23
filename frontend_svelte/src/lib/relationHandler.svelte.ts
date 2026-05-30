import type { SocketIO, SocketioStatus } from '$lib/socketio.svelte';
import type { AnyEntityExtended, Hierarchy } from '$lib/types.d.ts';

/**
 * A child that has been submitted but not yet acknowledged by the backend.
 * The preliminary `new_...` id is matched against `status.submitted_id` to
 * promote the entry into `linked` with its server-assigned id.
 */
export type PendingChild<TChild extends AnyEntityExtended> = {
	id: string;
	entity: TChild;
};

/**
 * Per-child-type configuration for `RelationHandler`. One spec per child type;
 * a single `RelationHandler` may hold several (e.g. groups, users, resources).
 *
 * Only internal app types belong here — adapt external-provider shapes
 * (Microsoft Graph etc.) on the integration side before passing them in.
 */
export type ChildRelationSpec<TChild extends AnyEntityExtended> = {
	/** SocketIO instance for the child's own namespace. Owned by the caller. */
	socketio: SocketIO<TChild>;
	/**
	 * Initial linked children (from server preload, e.g. `data.thisParent.groups`).
	 * Evaluated inside a `$effect`; re-runs reseed `linked` on PageData changes.
	 */
	initial?: () => TChild[] | undefined | null;
	/** Override the id extractor; defaults to `(c) => c.id`. */
	getId?: (child: TChild) => string;
};

export type RelationHandlerOptions = {
	/** Default inheritance flag for `link` / `submit`; overridable per call. */
	defaultInherit?: boolean;
};

/** Reactive surface for one child relation, returned by `RelationHandler.child(key)`. */
export interface ChildRelationView<TChild extends AnyEntityExtended> {
	readonly linked: TChild[];
	readonly pending: PendingChild<TChild>[];
	readonly unlinked: TChild[];

	link(childId: string, options?: { inherit?: boolean }): void;
	unlink(childId: string): void;
	delete(childId: string): void;

	/** Returns the preliminary `new_...` id assigned to the submitted entity. */
	submit(entity: TChild, options?: { inherit?: boolean }): string;

	/**
	 * Either clone `template` for each suffix (appending to `name`), or submit
	 * each fully-formed entry as-is. Returns the preliminary ids in order.
	 */
	submitBulk(
		template: TChild,
		input: { suffixes: string[]; inherit?: boolean } | { entries: TChild[]; inherit?: boolean }
	): string[];

	/** Replace `linked` with a fresh snapshot (e.g. after route data changes). */
	reseed(next: TChild[] | undefined | null): void;

	move(childId: string, toIndex: number): void;
}

class ChildSlot<TChild extends AnyEntityExtended> implements ChildRelationView<TChild> {
	#linked = $state<TChild[]>([]);
	#pending = $state<PendingChild<TChild>[]>([]);
	#spec: ChildRelationSpec<TChild>;
	#parent: () => { id: string } | undefined;
	#defaultInherit: boolean;

	constructor(
		spec: ChildRelationSpec<TChild>,
		parent: () => { id: string } | undefined,
		defaultInherit: boolean
	) {
		this.#spec = spec;
		this.#parent = parent;
		this.#defaultInherit = defaultInherit;

		if (spec.initial) {
			$effect(() => {
				const next = spec.initial!();
				if (next) this.#linked = next;
			});
		}

		const sio = spec.socketio;

		sio.client.on('transferred', (data: TChild) => {
			const id = this.#idOf(data);
			const idx = this.#linked.findIndex((c) => this.#idOf(c) === id);
			if (idx > -1) {
				this.#linked = this.#linked.map((c, i) => (i === idx ? { ...c, ...data } : c));
			}
		});

		sio.client.on('deleted', (resourceId: string) => {
			this.#linked = this.#linked.filter((c) => this.#idOf(c) !== resourceId);
			this.#pending = this.#pending.filter((p) => p.id !== resourceId);
		});

		sio.client.on('status', (status: SocketioStatus) => {
			if (!('success' in status)) return;
			const parentId = this.#parent()?.id;

			if (status.success === 'created') {
				const pendingIdx = this.#pending.findIndex((p) => p.id === status.submitted_id);
				if (pendingIdx > -1) {
					const promoted = { ...this.#pending[pendingIdx].entity, id: status.id } as TChild;
					this.#linked = [...this.#linked, promoted];
					this.#pending = this.#pending.filter((_, i) => i !== pendingIdx);
				}
			} else if (status.success === 'linked') {
				if (!parentId || status.parent_id !== parentId) return;
				const moved = sio.entities.find((e) => this.#idOf(e) === status.id);
				if (moved && !this.#linked.some((c) => this.#idOf(c) === status.id)) {
					this.#linked = [...this.#linked, moved];
				}
				sio.entities = sio.entities.filter((e) => this.#idOf(e) !== status.id);
			} else if (status.success === 'unlinked') {
				if (!parentId || status.parent_id !== parentId) return;
				const moved = this.#linked.find((c) => this.#idOf(c) === status.id);
				if (moved && !sio.entities.some((e) => this.#idOf(e) === status.id)) {
					sio.entities = [moved, ...sio.entities];
				}
				this.#linked = this.#linked.filter((c) => this.#idOf(c) !== status.id);
			}
		});
	}

	#idOf(child: TChild): string {
		return this.#spec.getId ? this.#spec.getId(child) : child.id;
	}

	get linked(): TChild[] {
		return this.#linked;
	}
	get pending(): PendingChild<TChild>[] {
		return this.#pending;
	}
	get unlinked(): TChild[] {
		return this.#spec.socketio.entities.filter(
			(e) => !this.#linked.some((l) => this.#idOf(l) === this.#idOf(e))
		);
	}

	link(childId: string, options?: { inherit?: boolean }): void {
		const parentId = this.#parent()?.id;
		if (!parentId) return;
		const hierarchy: Hierarchy = {
			child_id: childId,
			parent_id: parentId,
			inherit: options?.inherit ?? this.#defaultInherit
		};
		this.#spec.socketio.linkEntities(hierarchy);
	}

	unlink(childId: string): void {
		const parentId = this.#parent()?.id;
		if (!parentId) return;
		this.#spec.socketio.unlinkEntities({ child_id: childId, parent_id: parentId });
		// Eager drop; `status:unlinked` will reconcile `socketio.entities`.
		this.#linked = this.#linked.filter((c) => this.#idOf(c) !== childId);
	}

	delete(childId: string): void {
		this.#spec.socketio.deleteEntity(childId);
	}

	submit(entity: TChild, options?: { inherit?: boolean }): string {
		const preliminaryId =
			entity.id && entity.id.startsWith('new_')
				? entity.id
				: 'new_' + Math.random().toString(36).substring(2, 9);
		const payload = { ...entity, id: preliminaryId } as TChild;
		this.#pending = [...this.#pending, { id: preliminaryId, entity: payload }];
		this.#spec.socketio.submitEntity(
			payload,
			this.#parent()?.id,
			options?.inherit ?? this.#defaultInherit
		);
		return preliminaryId;
	}

	submitBulk(
		template: TChild,
		input: { suffixes: string[]; inherit?: boolean } | { entries: TChild[]; inherit?: boolean }
	): string[] {
		const inherit = input.inherit ?? this.#defaultInherit;
		if ('suffixes' in input) {
			return input.suffixes.map((suffix) => {
				const entity = {
					...template,
					name: ((template as TChild & { name?: string }).name ?? '') + suffix
				} as TChild;
				return this.submit(entity, { inherit });
			});
		}
		return input.entries.map((entity) => this.submit(entity, { inherit }));
	}

	reseed(next: TChild[] | undefined | null): void {
		this.#linked = next ?? [];
	}

	move(_childId: string, _toIndex: number): void {
		// TBD: wire to SocketIO reorder once the backend emits a `reordered` status.
		// Today this is a no-op; callers can apply an optimistic local reorder if needed.
	}
}

/**
 * Orchestrates parent ↔ children relations across SocketIO namespaces.
 *
 * Composition only: never extends `SocketIO`. Each child type contributes its
 * own `SocketIO` instance via `ChildRelationSpec.socketio`. RelationHandler
 * attaches extra listeners on construction to keep `linked` / `pending` in sync.
 *
 * Lifecycle: instantiate during component initialization, inside `onMount`,
 * or inside another effect — same constraint as `SocketIO`, because the
 * `initial` thunk is read inside a `$effect`.
 *
 * Parent-side lifecycle (delete-redirect, refreshing parent fields on
 * `transferred`) stays on the page; RelationHandler only touches children.
 */
export class RelationHandler<
	TParent extends AnyEntityExtended,
	TChildren extends Record<string, AnyEntityExtended>
> {
	#slots: { [K in keyof TChildren]: ChildSlot<TChildren[K]> };

	constructor(
		parent: () => TParent | undefined,
		children: { [K in keyof TChildren]: ChildRelationSpec<TChildren[K]> },
		options: RelationHandlerOptions = {}
	) {
		const defaultInherit = options.defaultInherit ?? true;
		const slots = {} as { [K in keyof TChildren]: ChildSlot<TChildren[K]> };
		for (const key in children) {
			slots[key] = new ChildSlot(children[key], parent, defaultInherit);
		}
		this.#slots = slots;
	}

	child<K extends keyof TChildren>(key: K): ChildRelationView<TChildren[K]> {
		return this.#slots[key];
	}
}
