import type { Socket } from 'socket.io-client';
import { io } from 'socket.io-client';
import { getContext } from 'svelte';

import type { Action } from '$lib/accessHandler';
import type { AccessPolicy, AnyEntityExtended, BackendAPIConfiguration } from '$lib/types.d.ts';

export type SocketioConnection = {
	namespace?: string;
	cookie_session_id?: string;
	query_params?: Record<string, string | number | boolean>;
	// TBD: type the query_params to specific strings? They can be:
	// request-access-data?: boolean
	// identity-ids?: string // getting added to rooms
	// resource-ids?: string // getting added to room
	// parent-resource-id?: string // potentially getting added to room
};

export type SocketioStatus =
	| { success: 'created'; id: string; submitted_id: string }
	| { success: 'updated'; id: string }
	| { success: 'deleted'; id: string }
	| { success: 'shared'; id: string }
	| { success: 'unshared'; id: string }
	| { success: 'linked'; id: string; parent_id: string; inherit: boolean }
	| { success: 'unlinked'; id: string; parent_id: string }
	| { error: string };

/**
 * Toggle the auto-registered default listeners. Each defaults to `true`.
 * Set to `false` to disable a default handler (e.g. when you want to fully override it).
 * Extra listeners added via `socketio.client.on(...)` always run alongside enabled defaults.
 */
export type SocketIODefaultHandlers = {
	transferred?: boolean;
	deleted?: boolean;
	status?: boolean;
};

export type SocketIOOptions<T extends AnyEntityExtended> = {
	/**
	 * Thunk that yields the array of entities for SocketIO to manage. Evaluated inside a
	 * `$effect`, so it runs once on construction (seeding the internal entities array) and
	 * then re-runs whenever any reactive value it reads changes — typically `data.*` from
	 * SvelteKit's PageData after navigation, `invalidate`, or form actions.
	 *
	 * Reactivity is opt-in: if the thunk reads only non-reactive data (e.g. a captured local
	 * constant array), it simply seeds once and never re-runs. If the thunk returns
	 * `null`/`undefined`, the current entities are preserved.
	 */
	subscribeEntities?: () => T[] | undefined | null;
	/** Enable/disable auto-registered default listeners. All default to `true`. */
	defaultHandlers?: SocketIODefaultHandlers;
	/**
	 * Optional default field values for entities produced by {@link SocketIO.createPending}.
	 * Evaluated on every `createPending()` call so callers can vary the template over time
	 * (e.g. seeding a form with the currently-edited parent's defaults). If absent,
	 * `createPending()` returns just `{ id }`.
	 */
	pendingTemplate?: () => Partial<Omit<T, 'id'>>;
};

/**
 * Svelte 5 reactive wrapper around a Socket.IO client.
 *
 * Owns a deeply reactive `entities` array (via `$state`) and — by default — wires up
 * `transferred`, `deleted`, and `status` listeners to keep that array in sync with the server.
 *
 * Usage notes:
 * - Must be instantiated during component initialization, inside `onMount`, or inside another
 *   effect. Instantiating from an arbitrary async callback (setTimeout, fetch `.then`, etc.)
 *   will break the `$effect` registration.
 * - Callers can attach additional listeners via `instance.client.on(event, cb)` — Socket.IO
 *   supports multiple listeners per event and they will run alongside the defaults.
 * - To fully override a default handler, disable it via `options.defaultHandlers.{event}: false`
 *   and register your own listener. The matching `handle*` methods remain public so custom
 *   listeners can still delegate to them if desired.
 */
export class SocketIO<T extends AnyEntityExtended = AnyEntityExtended> {
	public client: Socket;

	#entities = $state<T[]>([]);
	#pendingEntities = $state<T[]>([]);
	#pendingTemplate?: () => Partial<Omit<T, 'id'>>;

	constructor(connection: SocketioConnection, options: SocketIOOptions<T> = {}) {
		const backendAPIConfiguration: BackendAPIConfiguration = getContext('backendAPIConfiguration');
		const backendFqdn = backendAPIConfiguration.backendFqdn;
		const socketioServerUrl = backendFqdn.startsWith('localhost')
			? `http://${backendFqdn}`
			: `https://${backendFqdn}`;

		this.client = io(socketioServerUrl + connection.namespace, {
			path: backendAPIConfiguration.socketIOPath || `/socketio/v1`,
			auth: { 'session-id': connection.cookie_session_id },
			query: connection.query_params || {},
			forceNew: true
		});

		if (options.subscribeEntities) {
			$effect(() => {
				const next = options.subscribeEntities!();
				if (next) this.#entities = next;
			});
		}

		this.#pendingTemplate = options.pendingTemplate;

		const enableHandlers = options.defaultHandlers ?? {};
		if (enableHandlers.transferred !== false) {
			this.client.on('transferred', (data: T) => this.handleTransferred(data));
		}
		if (enableHandlers.deleted !== false) {
			this.client.on('deleted', (id: string) => this.handleDeleted(id));
		}
		if (enableHandlers.status !== false) {
			this.client.on('status', (data: SocketioStatus) => this.handleStatus(data));
		}

		this.client.connect();
	}

	// --- reactive surface ---
	/** Deeply reactive array of entities. Read in templates, mutate in place, or reassign. */
	get entities(): T[] {
		return this.#entities;
	}
	set entities(value: T[]) {
		this.#entities = value;
	}

	/** Reactive collection of entities that are being prepared but not yet submitted. */
	get pendingEntities(): T[] {
		return this.#pendingEntities;
	}
	set pendingEntities(value: T[]) {
		this.#pendingEntities = value;
	}

	// --- emitters ---
	/**
	 * Produce a fresh form-seed entity with a preliminary `new_*` id (which the backend
	 * swaps for a real UUID on `status:created`, at which point {@link handleStatus}
	 * rewrites it in place). Merges, in order: the configured `pendingTemplate` (if any),
	 * then the optional `overrides` argument, then the freshly-generated id.
	 *
	 * Does not touch `entities` — callers either wrap the result in `$state(...)` to bind
	 * to form inputs and submit via {@link submitEntity} when ready, or hand the overrides
	 * straight through `RelationHandler.submit`, which calls this internally.
	 */
	createPending(overrides?: Partial<T>): T {
		const template = this.#pendingTemplate?.() ?? {};
		const pendingEntity = {
			...template,
			...overrides,
			id: 'new_' + Math.random().toString(36).substring(2, 9)
		} as T;
		this.#pendingEntities.unshift(pendingEntity);
		return pendingEntity;
	}

	/**
	 * Submits an entity. The backend decides whether it is a create or an update
	 * based on whether `entity.id` is a UUID or a preliminary `new_*` id.
	 *
	 * When called without `entity`, the first entry in {@link pendingEntities} is submitted and
	 * a fresh pending entity is created automatically afterwards so form bindings remain valid.
	 * When `entity` is provided explicitly, the caller is responsible for refilling the pending
	 * slot if desired.
	 */
	submitEntity(
		entity?: T,
		parent_id?: string,
		inherit?: boolean,
		publicAccess?: boolean,
		publicAction?: Action
	): void {
		// TBD: refactor to check why (undfined, ...)
		// does not work and submits an empty payload,
		// instead of the first pending entity as intended.
		// TBD: consider autoSubmit based
		// on the id == 'new_*' pattern instead of presence of the entity argument?
		const autoSubmit = entity === undefined;
		const target = autoSubmit ? this.#pendingEntities[0] : entity;
		if (!target) return;
		this.client.emit('submit', {
			payload: target,
			...(parent_id ? { parent_id } : {}),
			...(inherit ? { inherit } : {}),
			...(publicAccess ? { public: publicAccess } : {}),
			...(publicAction ? { public_action: publicAction } : {})
		});
		// If auto-submitting, immediately create a fresh pending entity
		// to replace the one just submitted,
		// so form bindings remain valid.
		if (autoSubmit) this.createPending();
	}

	/**
	 * Submits all current {@link pendingEntities} in order. Shared options apply to every
	 * submission. The pending list is not automatically refilled afterwards.
	 */
	submitBulk(
		parent_id?: string,
		inherit?: boolean,
		publicAccess?: boolean,
		publicAction?: Action
	): void {
		for (const pending of [...this.#pendingEntities]) {
			// TBD: refactor to use submitEntity
			this.client.emit('submit', {
				payload: pending,
				...(parent_id ? { parent_id } : {}),
				...(inherit ? { inherit } : {}),
				...(publicAccess ? { public: publicAccess } : {}),
				...(publicAction ? { public_action: publicAction } : {})
			});
		}
	}

	deleteEntity(entityId: string): void {
		if (entityId.slice(0, 4) === 'new_') {
			// If the resource is new and has no id, we can just remove it from the local array
			const index = this.#pendingEntities.findIndex((entity) => entity.id === entityId);
			if (index > -1) this.#pendingEntities.splice(index, 1);
		} else {
			this.client.emit('delete', entityId);
		}
	}

	shareEntity(accessPolicy: AccessPolicy): void {
		this.client.emit('share', accessPolicy);
	}

	// --- default receivers (also usable from custom listeners) ---
	handleTransferred(data: T): void {
		const existingIndex = this.#entities.findIndex((entity) => entity.id === data.id);
		if (existingIndex > -1) {
			// Update existing entity in place
			this.#entities[existingIndex] = { ...this.#entities[existingIndex], ...data };
		} else {
			// Add new entity at the beginning (most recent first);
			this.#entities.unshift(data);
		}
	}

	handleDeleted(resource_id: string): void {
		const index = this.#entities.findIndex((entity) => entity.id === resource_id);
		if (index > -1) this.#entities.splice(index, 1);
	}

	handleStatus(status: SocketioStatus): void {
		if ('success' in status) {
			if (status.success === 'created') {
				// Move the pending draft into entities under its real server-assigned id.
				// Object identity is preserved (id mutated in place) so any held references
				// (e.g. editIds, form bindings) keep pointing at the same object.
				const pendingIndex = this.#pendingEntities.findIndex(
					(pendingEntity) => pendingEntity.id === status.submitted_id
				);
				if (pendingIndex > -1) {
					const [entity] = this.#pendingEntities.splice(pendingIndex, 1);
					entity.id = status.id;
					this.#entities.unshift(entity);
				}
			} else if (status.success === 'shared' || status.success === 'unshared') {
				// Re-read to resolve remaining inherited access. If none, the server emits `deleted`.
				this.client.emit('read', status.id);
			}
		}
	}
}
