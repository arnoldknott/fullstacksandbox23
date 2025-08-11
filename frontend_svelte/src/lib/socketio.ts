// import { getContext } from 'svelte';
import { io } from 'socket.io-client';
import type { Socket } from 'socket.io-client';
import { getContext } from 'svelte';
import type { AccessPolicy, AnyEntityExtended, BackendAPIConfiguration } from '$lib/types.d.ts';

export type SocketioConnection = {
	namespace?: string;
	cookie_session_id?: string;
	query_params?: Record<string, string | number | boolean>; // Query parameters to be sent to the server, e.g. for filtering or other purposes.
	// can be:
	// request-access-data?: boolean
	// identity-id?: string // getting added to rooms
	// resource-id?: string // getting added to room
	// parent-resource-id?: string // potentially getting added to room?
};

export type SocketioStatus =
	| { success: 'created'; id: string; submitted_id: string }
	| { success: 'updated'; id: string }
	| { success: 'deleted'; id: string }
	| { success: 'shared'; id: string }
	| { success: 'unshared'; id: string }
	| { error: string };

export class SocketIO {
	public client: Socket;
	// TBD: consider passing the entities at instantiation?
	private entities: AnyEntityExtended[] = [];

	constructor(connection: SocketioConnection, entities: AnyEntityExtended[] = []) {
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
		});
		// TBD: consider passing the entities at instantiation?
		this.entities = entities;
		this.client.connect();
	}

	// Emitters:
	public addEntity(newEntity: AnyEntityExtended): void {
		this.entities.unshift(newEntity);
	}

	public deleteEntity(entityId: string, editIds?: Set<string>): void {
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
		if (editIds) {
			if (editIds.has(entityId)) {
				editIds.delete(entityId);
				editIds = new Set(editIds); // trigger reactivity
			}
		}
	}

	public submitEntity(entity: AnyEntityExtended, editIds?: Set<string>): void {
		if (editIds) {
			if (entity.id.slice(0, 4) === 'new_') {
				editIds.delete(entity.id);
				editIds = new Set(editIds); // trigger reactivity
			}
		}
		this.client.emit('submit', { payload: entity });
	}

	public shareEntity(accessPolicy: AccessPolicy): void {
		this.client.emit('share', accessPolicy);
	}

	// Receivers:
	public receivers(editIds?: Set<string>): void {
		this.client.on('transfer', (data: AnyEntityExtended) => {
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
		});
		this.client.on('deleted', (resource_id: string) => {
			const index = this.entities.findIndex((entity) => entity.id === resource_id);
			if (index > -1) {
				this.entities.splice(index, 1);
			}
			// Creates a new array and breaks reactivity:
			// this.entities = this.entities.filter((entity) => entity.id !== resource_id);
		});
		this.client.on('status', (data: SocketioStatus) => {
			if ('success' in data) {
				if (data.success === 'created') {
					this.entities.forEach((entity) => {
						if (entity.id === data.submitted_id) {
							entity.id = data.id;
						}
						if (editIds) {
							editIds.add(data.id); // keep editing on after newly created resources
							editIds = new Set(editIds); // trigger reactivity
						}
					});
				} else if (data.success === 'shared') {
					this.client.emit('read', data.id);
				} else if (data.success === 'unshared') {
					// Re-read to see, if there is still access to the resource any other way,
					// for example inherited access.
					// if not, server emits a 'deleted' event.
					this.client.emit('read', data.id);
				}
			}
		});
	}
}
