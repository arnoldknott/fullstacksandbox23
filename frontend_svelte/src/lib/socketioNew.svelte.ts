import { io, type ManagerOptions, type Socket, type SocketOptions } from 'socket.io-client';
import { getContext } from 'svelte';

import { Action } from './accessHandler';
import {
	EntityContainer,
	type EntityContainerConfiguration,
	type EntityContainerInterface
} from './entityContainer.svelte';
import type {
	AccessPolicy,
	AnyEntityExtended,
	BackendAPIConfiguration,
	Hierarchy
} from './types.d.ts';

/**
 * Match backend configuration of what is read on connect
 */
type QueryParameters = {
	'request-access-data'?: boolean;
	'identity-ids'?: string;
	'resource-ids'?: string;
	'parent-id'?: string;
	'join-admin-room'?: boolean;
};

/**
 * Adhere to Partial<ManagerOptions & SocketOptions> from socket.io-client.
 */
export type SocketioConnection = {
	namespace?: string;
	sessionId?: string;
	parentId?: string;
	queryParams?: Omit<QueryParameters, 'parent-id'>; // parent-id is handled in the connection!
	overrides?: Partial<ManagerOptions & SocketOptions>;
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

// /**
//  * Functions that provide the Data for class SocketIO to manage. Evaluated inside a
//  * `$effect`, so it runs once on construction (seeding the internal entities array) and
//  * then re-runs whenever any reactive value it reads changes — typically `data.*` from
//  * SvelteKit's PageData after navigation, `invalidate`, or form actions.
//  */
// type SocketioData<T> = {
// 	seedEntities?: () => T[];
// 	seedPendingEntities?: () => T[];
// 	seedAccessPolicies?: () => Record<string, AccessPolicy[]>;
// 	seedAccessRights?: () => Record<string, Action>;
// 	seedHierarchies?: () => Hierarchy[];
// 	seedSelections?: () => Record<string, string[]>;
// 	// parentId?: string; // in connection!
// };

/**
 * Either disable via boolean or override via callback
 */
type SocketioHandlers<T> = {
	transferred?: boolean | ((data: T) => void);
	deleted?: boolean | ((resourceId: string) => void);
	status?: boolean | ((status: SocketioStatus) => void);
};

/**
 * For managing new entities before submitting them to the backend,
 * they are alive in the frontend only and
 * SocketIO holds space for them.
 */
// type pendingConfiguration<T extends AnyEntityExtended = AnyEntityExtended> = {
// 	// parentId?: string; // in connection!
// 	inherit?: boolean;
// 	public?: boolean;
// 	publicAction?: Action;
// 	template?: Partial<Omit<T, 'id'>>;
// };

export class SocketIO<T extends AnyEntityExtended = AnyEntityExtended>
	extends EntityContainer<T>
	implements EntityContainerInterface<T>
{
	public client: Socket;
	// #entities = $state<T[]>([]); // AnyEntityExtended[];
	// #pendingEntities = $state<T[]>([]); // AnyEntityExtended[];
	// #accessPolicies = $state<Record<string, AccessPolicy[]>>({}); // UUID: AccessPolicy[]
	// #accessRights = $state<Record<string, Action>>({}); // UUID: Action
	// #hierarchies = $state<Hierarchy[]>([]); // flat array of all hierarchies
	// #selections = $state<Record<string, string[]>>({}); // selectionName: entityIds[]
	// parentId?: string | null;
	// defaultInherit: boolean = false;
	// defaultPublic: boolean = false;
	// defaultPublicAction: Action = Action.READ;
	// pendingTemplate?: Partial<Omit<T, 'id'>>; // AnyEntityExtended without id;

	constructor(
		connection: SocketioConnection,
		configuration: Partial<
			Omit<EntityContainerConfiguration<T>, 'parentId'> & SocketioHandlers<T>
		> = {}
	) {
		super({ parentId: connection.parentId, ...configuration });
		const backendAPIConfiguration: BackendAPIConfiguration = getContext('backendAPIConfiguration');
		const backendFqdn = backendAPIConfiguration.backendFqdn;
		const socketioServerUrl = backendFqdn.startsWith('localhost')
			? `http://${backendFqdn}`
			: `https://${backendFqdn}`;

		const queryParams: QueryParameters = connection.queryParams ?? {};
		if (connection.parentId) {
			queryParams['parent-id'] = connection.parentId;
		}

		this.client = io(socketioServerUrl + connection.namespace, {
			path: backendAPIConfiguration.socketIOPath,
			auth: { 'session-id': connection.sessionId },
			query: queryParams,
			forceNew: true,
			...connection.overrides
		});

		// // TBD: do we need a function to seed the data (and first time use it here)
		// // for re-seeding or is it enough to do this through the setter?
		// $effect(() => {
		// 	this.#entities = configuration.seedEntities ? configuration.seedEntities() : [];
		// 	this.#pendingEntities = configuration.seedPendingEntities
		// 		? configuration.seedPendingEntities()
		// 		: [];
		// 	this.#accessPolicies = configuration.seedAccessPolicies
		// 		? configuration.seedAccessPolicies()
		// 		: {};
		// 	this.#accessRights = configuration.seedAccessRights ? configuration.seedAccessRights() : {};
		// 	this.#hierarchies = configuration.seedHierarchies ? configuration.seedHierarchies() : [];
		// 	this.#selections = configuration.seedSelections ? configuration.seedSelections() : {};
		// });
		// this.parentId = connection.parentId ?? undefined;
		// this.pendingTemplate = configuration.template ?? undefined; // TBD: change into setting all values, but the id value to null/undifned/empty, whatver is adequate - note the mandartory keys!

		// if handlers are not disabled, add the provided handler or the default one:
		if (configuration.transferred !== false) {
			this.client.on('transferred', (data: T) => {
				if (typeof configuration.transferred === 'function') {
					configuration.transferred(data);
				} else {
					this.handleTransferred(data);
				}
			});
		}
		if (configuration.deleted !== false) {
			this.client.on('deleted', (id: string) => {
				if (typeof configuration.deleted === 'function') {
					configuration.deleted(id);
				} else {
					this.handleDeleted(id);
				}
			});
		}
		if (configuration.status !== false) {
			this.client.on('status', (status: SocketioStatus) => {
				if (typeof configuration.status === 'function') {
					configuration.status(status);
				} else {
					this.handleStatus(status);
				}
			});
		}
	}

	// // --- reactive surface ---
	// /**
	//  * Getters and Setters for the main entities array managed by this SocketIO instance.
	//  *
	//  * Deeply reactive array of entities managed by this socketio class.
	//  * Read in templates, mutate in place, or reassign.
	//  */
	// get entities(): T[] {
	// 	return this.#entities;
	// }
	// set entities(value: T[]) {
	// 	this.#entities = value;
	// }

	// /** Reactive collection of entities that are being prepared but not yet submitted. */
	// get pendingEntities(): T[] {
	// 	return this.#pendingEntities;
	// }
	// set pendingEntities(value: T[]) {
	// 	this.#pendingEntities = value;
	// }

	// get accessPolicies(): Record<string, AccessPolicy[]> {
	// 	return this.#accessPolicies;
	// }
	// set accessPolicies(value: Record<string, AccessPolicy[]>) {
	// 	this.#accessPolicies = value;
	// }

	// get accessRights(): Record<string, Action> {
	// 	return this.#accessRights;
	// }
	// set accessRights(value: Record<string, Action>) {
	// 	this.#accessRights = value;
	// }

	// get hierarchies(): Hierarchy[] {
	// 	return this.#hierarchies;
	// }
	// set hierarchies(value: Hierarchy[]) {
	// 	this.#hierarchies = value;
	// }

	// get selections(): Record<string, string[]> {
	// 	return this.#selections;
	// }
	// set selections(value: Record<string, string[]>) {
	// 	this.#selections = value;
	// }

	// /**
	//  * Produce a new entity with a preliminary `new_*` id (which the backend
	//  * swaps for a real UUID on `status:created`, at which point {@link handleStatus}
	//  * rewrites it in place). Merges, in order: the configured `pendingTemplate` (if any),
	//  * then the optional `overrides` argument, then the freshly-generated id.
	//  *
	//  * Does not touch `entities` — callers either wrap the result in `$state(...)` to bind
	//  * to form inputs and submit via {@link submitEntity} when ready.
	//  */
	// createPending(overrides?: Partial<T>): T {
	// 	const pendingEntity = {
	// 		...this.pendingTemplate,
	// 		...overrides,
	// 		id: 'new_' + Math.random().toString(36).substring(2, 9)
	// 	} as T;
	// 	this.#pendingEntities.unshift(pendingEntity);
	// 	return pendingEntity;
	// }

	// // TBD: consider moving the Selection in its own class and here?

	// /**
	//  * Selections are named subsets of the main entity-id array, stored as arrays of ids.
	//  *
	//  * Deeply reactive array of an array of ids.
	//  * Read in templates, mutate in place, or reassign.
	//  * Use cases for selections might include:
	//  * - marking the entities, that are editable in browser
	//  * - marking the entities that are selected in a list for bulk actions
	//  * - order of entities, that are sorted by a specific entity attribute
	//  * - select by access policies: all entities that are shared with a specific team with a specific right, etc.
	//  * - select by access rights: all entities that the user has 'own', 'write', 'connect' 'read' access to, etc.
	//  * - select by hierarchy: all entities that are linked to a specific parent entity or have a specific child entity, etc.
	//  */
	// addSelection(name: string, entityIds: string[]) {
	// 	if (this.#selections[name]) {
	// 		throw new Error(`Selection with name "${name}" already exists.`);
	// 	}
	// 	this.#selections[name] = entityIds;
	// 	return this.#selections[name];
	// }

	// // getSelection(name: string) {
	// //     if (!this.#selections[name]) {
	// //         throw new Error(`Selection with name "${name}" does not exist.`);
	// //     }
	// //     return this.#selections[name];
	// // }

	// getSelectedEntities(name: string) {
	// 	const selectedIds = this.selections[name];
	// 	return this.entities.filter((entity) => selectedIds.includes(entity.id));
	// }

	// addToSelection(name: string, entityIds: string[]) {
	// 	if (!this.#selections[name]) {
	// 		throw new Error(`Selection with name "${name}" does not exist.`);
	// 	}
	// 	this.#selections[name] = [...this.#selections[name], ...entityIds];
	// 	return this.#selections[name];
	// }

	// removeFromSelection(name: string, entityIds: string[]) {
	// 	if (!this.#selections[name]) {
	// 		throw new Error(`Selection with name "${name}" does not exist.`);
	// 	}
	// 	this.#selections[name] = this.#selections[name].filter((id) => !entityIds.includes(id));
	// 	return this.#selections[name];
	// }

	// /** for example all entities that match a specific condition */
	// // TBD extend with choosing different data containers, such as
	// // accessPolicies, hierarchies, etc. for more complex selection logic,
	// // e.g. select all entities that are shared with a specific team with a specific right,
	// // or select all entities that are linked to a specific parent entity or have a specific child entity, etc.
	// createFilteredSelection(name: string, filterFn: (entity: T) => boolean) {
	// 	const filteredIds = this.entities.filter(filterFn).map((entity) => entity.id);
	// 	return this.addSelection(name, filteredIds);
	// }

	// createAllLinkedSelection(name: string, parentId: string) {
	// 	const linkedIds =
	// 		this.#hierarchies.filter((h) => h.parent_id === parentId).map((h) => h.child_id) || [];
	// 	return this.addSelection(name, linkedIds);
	// }

	// sortSelectionBy(name: string, attribute: keyof T, ascending = true) {
	// 	this.entities.sort((a, b) => {
	// 		if (a[attribute] < b[attribute]) return ascending ? -1 : 1;
	// 		if (a[attribute] > b[attribute]) return ascending ? 1 : -1;
	// 		return 0;
	// 	});
	// 	this.#selections[name] = this.getSelectedEntities(name).map((entity) => entity.id);
	// }

	/**
	 * Submits an entity. The backend decides whether it is a create or an update
	 * based on whether `entity.id` is a UUID or a preliminary `new_*` id.
	 *
	 * When called without `entity`, the first entry in {@link pendingEntities} is submitted and
	 * a fresh pending entity is created automatically afterwards
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
		const target = autoSubmit ? this.pendingEntities[0] : entity;
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
		for (const pending of [...this.pendingEntities]) {
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

	/**
	 * Deletes an entity by id. If the id is a preliminary `new_*` id,
	 * it is removed from the local `pendingEntities` array.
	 * Otherwise, a delete event is emitted to the backend,
	 * which then emits `deleted` to all clients (including this one)
	 * to trigger removal from the main `entities` array.
	 */
	deleteEntity(entityId: string): void {
		if (entityId.slice(0, 4) === 'new_') {
			// If the resource is new and has no id, we can just remove it from the local array
			const index = this.pendingEntities.findIndex((entity) => entity.id === entityId);
			if (index > -1) this.pendingEntities.splice(index, 1);
		} else {
			this.client.emit('delete', entityId);
		}
	}

	/**
	 * Creates a hierarchy link between a child and a parent entity.
	 * If no parentId is provided, it defaults to the current `parentId` of this SocketIO instance (if any).
	 * The `inherit` flag indicates whether the child should inherit access policies from the parent.
	 * Reconciliation of the new hierarchy happens in the `status:linked` handler, which updates the local state based on server confirmation.
	 */
	link(childId: string, parentId: string = this.parentId ?? '', inherit?: boolean): void {
		if (parentId) {
			const hierarchy: Hierarchy = {
				child_id: childId,
				parent_id: parentId || this.parentId || '', // in creating a link, this should never be empty, but we need to satisfy the type
				inherit: inherit ?? this.pendingSubmitOptions?.inherit
			};
			this.client.emit('link', hierarchy);
		}
		// Reconciliation happens in the `status:linked` handler.
	}

	/**
	 * Removes a hierarchy link between a child and a parent entity.
	 * If no parentId is provided, it defaults to the current `parentId`
	 * of this SocketIO instance (if any) or removes the child from all parents.
	 * Reconciliation of the removed hierarchy happens in the `status:unlinked`
	 * handler, which updates the local state based on server confirmation.
	 */
	unlink(childId: string, parentId: string = this.parentId ?? ''): void {
		console.log('=== unlinking: ', { childId, parentId }, ' ===');
		if (parentId) {
			this.client.emit('unlink', { child_id: childId, parent_id: parentId });
		} else {
			throw new Error(
				"Parent ID must be provided either as an argument or as the EntityContainer's parentId property."
			);
		}
		// Reconciliation happens in the `status:unlinked` handler.
	}
	/**
	 * TBD: implement changeLink() - also missing in backend!
	 */
	changeLink(_childId: string, _parentId?: string, _inherit?: boolean): void {}

	/**
	 * TBD: Re-order children - also missing in backend!
	 */
	move(
		_childId: string,
		_postion: 'before' | 'after' | 'start' | 'end',
		_parentId?: string,
		_otherChildId?: string
	): void {}

	/**
	 * Shares, updates access rights or removes sharing of an entity based on the provided access policy.
	 * The backend emits `status:shared` or `status:unshared` to all clients (including this one)
	 * to trigger re-reading of the entity and update of the local state based on server confirmation.
	 */
	shareEntity(accessPolicy: AccessPolicy): void {
		this.client.emit('share', accessPolicy);
	}

	/**
	 * Default Handlers for Receiving Events from the Server via Socket.IO
	 *
	 * Default receivers for socket events, can be used as-is or dissabled or overridden
	 * by providing a custom handler in the constructor config.
	 */
	handleTransferred(data: T): void {
		const existingIndex = this.entities.findIndex((entity) => entity.id === data.id);
		if (existingIndex > -1) {
			// Update existing entity in place
			this.entities[existingIndex] = { ...this.entities[existingIndex], ...data };
			this.accessPolicies[this.entities[existingIndex].id] = data.access_policies
				? data.access_policies
				: this.accessPolicies[this.entities[existingIndex].id];
			this.accessRights[this.entities[existingIndex].id] = data.access_right
				? data.access_right
				: this.accessRights[this.entities[existingIndex].id];
			this.children[this.entities[existingIndex].id] = data.children
				? data.children
				: this.children[this.entities[existingIndex].id];
			this.parents[this.entities[existingIndex].id] = data.parents
				? data.parents
				: this.parents[this.entities[existingIndex].id];
		} else {
			// Add new entity at the beginning (most recent first);
			this.entities.unshift(data);
			this.accessPolicies[data.id] = data.access_policies ?? [];
			this.accessRights[data.id] = data.access_right ?? Action.READ;
			this.children[data.id] = data.children ?? [];
			this.parents[data.id] = data.parents ?? [];
		}
	}

	handleDeleted(resource_id: string): void {
		const index = this.entities.findIndex((entity) => entity.id === resource_id);
		if (index > -1) this.entities.splice(index, 1);
		// remove from selections:
		for (const selectionName in this.selections) {
			// TBD: consider using getters and setters,
			// i.e. this.selections[selectionName] = this.selections[selectionName].filter(...)
			// to trigger reactivity?
			this.selections[selectionName] = this.selections[selectionName].filter(
				(id) => id !== resource_id
			);
		}
		// remove from hierarchies:
		// this.hierarchies = this.hierarchies.filter(
		// 	(h) => h.child_id !== resource_id && h.parent_id !== resource_id
		// );
		delete this.accessPolicies[resource_id];
		delete this.accessRights[resource_id];
		delete this.children[resource_id];
		delete this.parents[resource_id];
		// TBD: consider also removing from accessPolicies and accessRights, depending on the backend implementation and emitted data on delete.
	}

	handleStatus(status: SocketioStatus): void {
		if ('success' in status) {
			if (status.success === 'created') {
				// Move the pending draft into entities under its real server-assigned id.
				// Object identity is preserved (id mutated in place) so any held references
				// (e.g. editIds, form bindings) keep pointing at the same object.
				const pendingIndex = this.pendingEntities.findIndex(
					(pendingEntity) => pendingEntity.id === status.submitted_id
				);
				if (pendingIndex > -1) {
					const [entity] = this.pendingEntities.splice(pendingIndex, 1);
					entity.id = status.id;
					this.entities.unshift(entity);
				}
				// replace submitted_id with id in all selections, as it is now replaced by the real id
				for (const selectionName in this.selections) {
					// TBD: consider using getters and setters,
					// i.e. this.selections[selectionName] = this.selections[selectionName].map(...)
					// to trigger reactivity?
					this.selections[selectionName] = this.selections[selectionName].map((id) =>
						id === status.submitted_id ? status.id : id
					);
				}
			} else if (status.success === 'shared' || status.success === 'unshared') {
				// Re-read to resolve remaining inherited access. If none, the server emits `deleted`.
                // TBD: or consider sending the updated access at share from backend?
				this.client.emit('read', status.id);
			} else if (status.success === 'linked') {
				// if (!parentId || status.parent_id !== parentId) return;
				// if (!this.hierarchies.some((h) => h.child_id === status.id)) {
				// 	this.hierarchies = [
				// 		...this.hierarchies,
				// 		{ child_id: status.id, parent_id: parentId, inherit: status.inherit }
				// 	];
				// }
                // Re-read to resolve updated hierarchy
                // TBD: or consider sending the updated hierarchy at link from backend?
                this.client.emit('read', status.id);
			} else if (status.success === 'unlinked') {
				// if (!parentId || status.parent_id !== parentId) return;
				// this.hierarchies = this.hierarchies.filter((h) => h.child_id !== status.id);
                // Re-read to resolve updated hierarchy
                // TBD: or consider sending the updated hierarchy at unlink from backend?
                this.client.emit('read', status.id);
			}
		}
	}
}
