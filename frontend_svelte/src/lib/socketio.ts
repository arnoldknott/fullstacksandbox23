// import { getContext } from 'svelte';
import { io } from 'socket.io-client';
import type { Socket } from 'socket.io-client';
import { getContext } from 'svelte';
import type {
	AccessPolicy,
	AnyEntityExtended,
	BackendAPIConfiguration,
	Hierarchy
} from '$lib/types.d.ts';
import type { Action } from '$lib/accessHandler';
import { SvelteSet } from 'svelte/reactivity';

export type SocketioConnection = {
	namespace?: string;
	cookie_session_id?: string;
	query_params?: Record<string, string | number | boolean>; // Query parameters to be sent to the server, e.g. for filtering or other purposes.
	// can be:
	// request-access-data?: boolean
	// identity-ids?: string // getting added to rooms
	// resource-ids?: string // getting added to room
	// parent-resource-id?: string // potentially getting added to room?
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

export class SocketIO {
	public client: Socket;
	private entities: AnyEntityExtended[] = [];
	private editIds?: SvelteSet<string>;

	constructor(
		connection: SocketioConnection,
		getEntities?: () => AnyEntityExtended[],
		getEditIds?: () => SvelteSet<string>
	) {
		// TBD: put a try catch here?
		const backendAPIConfiguration: BackendAPIConfiguration = getContext('backendAPIConfiguration');
		const backendFqdn = backendAPIConfiguration.backendFqdn;
		const socketioServerUrl = backendFqdn.startsWith('localhost')
			? `http://${backendFqdn}`
			: `https://${backendFqdn}`;
		// Before sending the session_id, make sure to acquire a token silently on server side to update the cache!
		this.client = io(socketioServerUrl + connection.namespace, {
			path: `/socketio/v1`,
			auth: { 'session-id': connection.cookie_session_id },
			// TBD: refactor into an object to allow more flexible query parameters?
			query: connection.query_params || {} // Use the query_params from the connection object
			// forceNew: true, // to avoid reusing existing connections and get clients in the same room. TBD: consider an override option ("reuseExisting")?
			// multiplex: false // to avoid reusing existing connections and get clients in the same room. TBD: consider an override option ("reuseExisting")?
		});
		this.entities = getEntities ? getEntities() : [];
		if (getEditIds) {
			this.editIds = getEditIds();
		}
		this.client.connect();
	}

	// Emitters:
	public addEntity(newEntity: AnyEntityExtended): void {
		this.entities.unshift(newEntity);
	}

	// The backend is handling it, whether it's new or existing.
	// If the id is a UUID, it tries to update an existing resource.
	public submitEntity(
		entity: AnyEntityExtended,
		parent_id?: string,
		inherit?: boolean,
		publicAccess?: boolean,
		publicAction?: Action
	): void {
		// Deletes the preliminary id from editIds, if it is a new entity.
		// if (this.editIds && this.editIds.has(entity.id) && entity.id.slice(0, 4) === 'new_') {
		if (this.editIds && this.editIds.has(entity.id) && entity.id.slice(0, 4) === 'new_') {
			this.editIds.delete(entity.id);
		}
		const data = {
			payload: entity,
			...(parent_id ? { parent_id } : {}),
			...(inherit ? { inherit } : {}),
			...(publicAccess ? { public: publicAccess } : {}),
			...(publicAction ? { public_action: publicAction } : {})
		};
		this.client.emit('submit', data);
	}

	public deleteEntity(entityId: string): void {
		if (entityId.slice(0, 4) === 'new_') {
			// If the resource is new and has no id, we can just remove it from the local array
			const index = this.entities.findIndex((entity) => entity.id === entityId);
			if (index > -1) {
				this.entities.splice(index, 1);
			}
			// Creates a new array and breaks reactivity:
			// this.entities = this.entities.filter((res) => res.id !== entityId);
		} else {
			this.client.emit('delete', entityId);
		}
	}

	public shareEntity(accessPolicy: AccessPolicy): void {
		this.client.emit('share', accessPolicy);
	}

	public linkEntities(hierarchy: Hierarchy): void {
		this.client.emit('link', hierarchy);
	}

	public unlinkEntities(hierarchy: Hierarchy): void {
		this.client.emit('unlink', hierarchy);
	}

	// Receivers:
	public handleTransferred(data: AnyEntityExtended): void {
		const existingIndex = this.entities.findIndex((entity) => entity.id === data.id);
		if (existingIndex > -1) {
			// Update existing entity in place
			this.entities[existingIndex] = { ...this.entities[existingIndex], ...data };
			// creates a new array and breaks reactivity:
			// this.entities = this.entities.map((entity) =>
			// 	// only replaces the keys, where the newly incoming data is defined.
			// 	entity.id === data.id ? { ...entity, ...data } : entity
			// );
		} else {
			// Add new entity
			this.entities.push(data);
		}
	}

	public handleDeleted(resource_id: string): void {
		const index = this.entities.findIndex((entity) => entity.id === resource_id);
		if (index > -1) {
			this.entities.splice(index, 1);
		}
		if (this.editIds) {
			this.editIds.delete(resource_id);
		}
		// Creates a new array and breaks reactivity:
		// this.entities = this.entities.filter((entity) => entity.id !== resource_id);
	}

	public handleStatus(status: SocketioStatus): void {
		if ('success' in status) {
			if (status.success === 'created') {
				if (this.editIds) {
					this.editIds.add(status.id);
				}

				this.entities.forEach((entity) => {
					if (entity.id === status.submitted_id) {
						entity.id = status.id;
					}
				});
				// Adds the created id (as a replacement for the prelimnary id) to editIds.
				// This is needed to keep editing on after newly created resources.
			} else if (status.success === 'shared') {
				this.client.emit('read', status.id);
			} else if (status.success === 'unshared') {
				// Re-read to see, if there is still access to the resource any other way,
				// for example inherited access.
				// if not, server emits a 'deleted' event.
				this.client.emit('read', status.id);
			}
		}
	}
}
