// import { getContext } from 'svelte';
import { io } from 'socket.io-client';
import type { Socket } from 'socket.io-client';
import { getContext } from 'svelte';
import type { AccessPolicy, AnyEntityExtended, BackendAPIConfiguration } from '$lib/types.d.ts';
import { SvelteSet } from 'svelte/reactivity';
import type { S } from 'vitest/dist/chunks/config.d.D2ROskhv.js';

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
	private editIds?: SvelteSet<string>;
	// private getEditIds?: () => Set<string>;

	constructor(
		connection: SocketioConnection,
		getEntities?: () => AnyEntityExtended[],
		// editIds?: SvelteSet<string>
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
		});
		// TBD: consider passing the entities at instantiation?
		this.entities = getEntities ? getEntities() : [];
		if (getEditIds) {
			this.editIds = getEditIds();
		}
		// this.editIds = editIds;
		this.client.connect();
	}

	// private get editIds(): Set<string> | undefined {
	// 	return this.getEditIds ? this.getEditIds() : undefined;
	// }

	public get getEditIds(): SvelteSet<string> {
		return this.editIds ? this.editIds : new SvelteSet<string>;
	}

	// Emitters:
	public addEntity(newEntity: AnyEntityExtended): void {
		console.log('=== socketio - adding entity ===');
		this.entities.unshift(newEntity);
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
		// Handling of deleting the editIds moved to receiver status - deleted,
		// so that other users, that were currently editing the same resource,
		// can also remove it from their editIds.
		// if (this.editIds) {
		// 	if (this.editIds.has(entityId)) {
		// 		this.editIds.delete(entityId);
		// 		this.editIds = new Set(this.editIds); // trigger reactivity
		// 	}
		// }
		// console.log('=== socketio - deleteEntity - editIds ===');
		// console.log(this.editIds);
		// if (this.editIds && this.editIds.has(entityId)) {
		// 	this.editIds.delete(entityId);
		// 	this.editIds = new SvelteSet(this.editIds); // trigger reactivity
		// }
	}

	public submitEntity(entity: AnyEntityExtended): void {
		// if (this.editIds) {
		// 	if (entity.id.slice(0, 4) === 'new_') {
		// 		this.editIds.delete(entity.id);
		// 		this.editIds = new Set(this.editIds); // trigger reactivity
		// 	}
		// }
		// console.log('=== socketio - submitEntity - editIds ===');
		// console.log(this.editIds);
		// Deletes the priliminary id from editIds, if it is a new entity.
		if (this.editIds && this.editIds.has(entity.id) && entity.id.slice(0, 4) === 'new_') {
			this.editIds.delete(entity.id);
			this.editIds = new SvelteSet(this.editIds); // trigger reactivity
		}
		this.client.emit('submit', { payload: entity });
	}

	public shareEntity(accessPolicy: AccessPolicy): void {
		this.client.emit('share', accessPolicy);
	}

	// Receivers:
	public receivers(): void {
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
			// TBD: debug reactivity:
			if (this.editIds) {
				// console.log('=== socketio - deleted - this.editIds ===');
				// console.log(this.editIds);
				this.editIds.delete(resource_id);
				this.editIds = new SvelteSet(this.editIds); // trigger reactivity
				// console.log('=== socketio - deleted - this.editIds - after deletion ===');
				// console.log(this.editIds);
			}
			// Creates a new array and breaks reactivity:
			// this.entities = this.entities.filter((entity) => entity.id !== resource_id);
		});
		this.client.on('status', (data: SocketioStatus) => {
			console.log('=== socketio - status - data ===');
			console.log(data);
			if ('success' in data) {
				if (data.success === 'created') {
					if (this.editIds) {
						// console.log('=== socketio - created - this.editIds ===');
						// console.log(this.editIds);
						this.editIds.add(data.id);
						this.editIds = new SvelteSet(this.editIds); // trigger reactivity
						// console.log('=== socketio - created - this.editIds - after addition ===');
						// console.log(this.editIds);
					}
					// console.log('=== socketio - created - data ===');
					// console.log(data);
					this.entities.forEach((entity) => {
						if (entity.id === data.submitted_id) {
							entity.id = data.id;
						}
					});
					// Adds the created id (as a replacement for the prelimnary id) to editIds.
					// This is needed to keep editing on after newly created resources.
					// TBD: debug reactivity:

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

	public handleTransfer(data: AnyEntityExtended): void {
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

	public handleDeleted(resource_id: string, editIds?: SvelteSet<string>): SvelteSet<string> {
		const index = this.entities.findIndex((entity) => entity.id === resource_id);
		if (index > -1) {
			this.entities.splice(index, 1);
		}
		// TBD: debug reactivity:
		if (editIds) {
			// console.log('=== socketio - deleted - this.editIds ===');
			// console.log(this.editIds);
			editIds.delete(resource_id);
			editIds = new SvelteSet(editIds); // trigger reactivity
			// console.log('=== socketio - deleted - this.editIds - after deletion ===');
			// console.log(this.editIds);
		}
		// Creates a new array and breaks reactivity:
		// this.entities = this.entities.filter((entity) => entity.id !== resource_id);
		return editIds ? editIds : new SvelteSet<string>();
	}

	public handleStatus(data: SocketioStatus, editIds?: SvelteSet<string>): SvelteSet<string> {
		if ('success' in data) {
			if (data.success === 'created') {
				if (editIds) {
					// console.log('=== socketio - created - this.editIds ===');
					// console.log(this.editIds);
					editIds.add(data.id);
					editIds = new SvelteSet(editIds); // trigger reactivity
					// console.log('=== socketio - created - this.editIds - after addition ===');
					// console.log(this.editIds);
				}
				// console.log('=== socketio - created - data ===');
				// console.log(data);
				this.entities.forEach((entity) => {
					if (entity.id === data.submitted_id) {
						entity.id = data.id;
					}
				});
				// Adds the created id (as a replacement for the prelimnary id) to editIds.
				// This is needed to keep editing on after newly created resources.
				// TBD: debug reactivity:

			} else if (data.success === 'shared') {
				this.client.emit('read', data.id);
			} else if (data.success === 'unshared') {
				// Re-read to see, if there is still access to the resource any other way,
				// for example inherited access.
				// if not, server emits a 'deleted' event.
				this.client.emit('read', data.id);
			}
		}
		return editIds ? editIds : new SvelteSet<string>();
	};
}

