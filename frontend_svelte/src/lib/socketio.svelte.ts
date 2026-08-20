import { io, type ManagerOptions, type Socket, type SocketOptions } from 'socket.io-client';
import { getContext } from 'svelte';

import { Action, PUBLIC_IDENTITY_ID } from './accessHandler';
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
	| { success: 'linked'; id: string; parent_id: string; inherit: boolean; order?: number }
	| { success: 'unlinked'; id: string; parent_id: string }
	| { error: string };

/**
 * Either disable via boolean or override via callback
 */
type SocketioHandlers<T> = {
	transferred?: boolean | ((data: T) => void);
	deleted?: boolean | ((resourceId: string) => void);
	status?: boolean | ((status: SocketioStatus) => void);
};

export type SocketioConfiguration<T extends AnyEntityExtended = AnyEntityExtended> = Partial<
	Omit<EntityContainerConfiguration<T>, 'parentId'> & SocketioHandlers<T>
>;

export class SocketIO<T extends AnyEntityExtended = AnyEntityExtended>
	extends EntityContainer<T>
	implements EntityContainerInterface<T>
{
	public client: Socket;

	constructor(connection: SocketioConnection, configuration: SocketioConfiguration<T> = {}) {
		super({ parentId: connection.parentId, ...configuration });
		const backendAPIConfiguration: BackendAPIConfiguration = getContext('backendAPIConfiguration');
		const backendFqdn = backendAPIConfiguration.backendFqdn;
		const socketioServerUrl = backendFqdn.startsWith('localhost')
			? `http://${backendFqdn}`
			: `https://${backendFqdn}`;

		const queryParams: QueryParameters = { ...(connection.queryParams ?? {}) };
		if (queryParams['identity-ids']) {
			// the public sentinel id is client-side only and has no backend room to join
			queryParams['identity-ids'] = queryParams['identity-ids']
				.split(',')
				.filter((identityId) => identityId !== PUBLIC_IDENTITY_ID)
				.join(',');
		}
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

		if (this.pendingTemplate) this.createPending();
		// simulate delay for testing UI elements like forms to create a new entity, that depend on the pendingEntity
		// if (this.pendingTemplate) {
		// 	setTimeout(() => {
		// 		this.createPending();
		// 	}, 3000);
		// }

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
		inherit?: boolean
		// publicAccess?: boolean,
		// publicAction?: Action
	): void {
		const autoSubmit = entity === undefined;
		const target = autoSubmit ? this.pendingEntities[0] : entity;
		if (!target) return;
		const newId = target.id.startsWith('new_') ? target.id : undefined;
		const access_policies = newId ? this.accessPolicies[target.id] : [];
		const hierarchies = newId ? this.hierarchies[target.id] : [];
		this.client.emit('submit', {
			payload: target,
			...(parent_id ? { parent_id } : {}),
			...(inherit ? { inherit } : {}),
			...(access_policies ? { access_policies: access_policies } : {}),
			...(hierarchies ? { hierarchies: hierarchies } : {})
			// ...(publicAccess ? { public: publicAccess } : {}),
			// ...(publicAction ? { public_action: publicAction } : {})
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
		inherit?: boolean
		// publicAccess?: boolean,
		// publicAction?: Action
	): void {
		for (const pending of [...this.pendingEntities]) {
			this.submitEntity(pending, parent_id, inherit);
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
			this.hierarchies[this.entities[existingIndex].id] = data.hierarchies
				? data.hierarchies
				: this.hierarchies[this.entities[existingIndex].id];
		} else {
			// Add new entity at the beginning (most recent first);
			this.entities.unshift(data);
			this.accessPolicies[data.id] = data.access_policies ?? [];
			this.accessRights[data.id] = data.access_right ?? Action.READ;
			this.hierarchies[data.id] = data.hierarchies ?? [];
		}
	}

	handleDeleted(resource_id: string): void {
		const index = this.entities.findIndex((entity) => entity.id === resource_id);
		if (index > -1) this.entities.splice(index, 1);
		// remove from selections:
		for (const selectionName in this.selections) {
			this.selections[selectionName] = this.selections[selectionName].filter(
				(id) => id !== resource_id
			);
		}
		delete this.accessPolicies[resource_id];
		delete this.accessRights[resource_id];
		delete this.hierarchies[resource_id];
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
					this.selections[selectionName] = this.selections[selectionName].map((id) =>
						id === status.submitted_id ? status.id : id
					);
				}
			} else if (status.success === 'shared' || status.success === 'unshared') {
				// Re-read to resolve remaining inherited access. If none, the server emits `deleted`.
				// TBD: or consider sending the updated access at share from backend?
				this.client.emit('read', status.id);
			} else if (status.success === 'linked') {
				if (status.parent_id === this.parentId) {
					const existingHierarchyIndex = this.hierarchies[status.id]?.findIndex(
						(hierarchy) =>
							hierarchy.child_id === status.id && hierarchy.parent_id === status.parent_id
					);
					if (existingHierarchyIndex > -1) {
						// Update existing hierarchy in place
						this.hierarchies[status.id][existingHierarchyIndex] = {
							child_id: status.id,
							parent_id: status.parent_id,
							inherit: status.inherit,
							order: status.order
						};
					} else {
						// Re-read the linked entity
						this.client.emit('read', status.id);
						// And add the new hierarchy link to the local state.
						// TBD: should this one be removed and leave it to the read reconciliation?
						this.hierarchies[status.id] = [
							{
								child_id: status.id,
								parent_id: this.parentId,
								inherit: status.inherit,
								order: status.order
							}
						];
					}
				}
			} else if (status.success === 'unlinked') {
				if (status.parent_id === this.parentId) {
					this.hierarchies[status.id] = this.hierarchies[status.id]?.filter(
						(h) => h.child_id !== status.id
					);
				}
			}
		}
		// TBD: consider handling status.error,
		// depending on the backend implementation and emitted data on error.
		// Maybe just console.logging for now?
	}
}
