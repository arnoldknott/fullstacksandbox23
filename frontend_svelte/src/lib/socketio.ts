// import { getContext } from 'svelte';
import { io } from 'socket.io-client';
import type { Socket } from 'socket.io-client';
import { getContext } from 'svelte';
import type { BackendAPIConfiguration } from '$lib/types.d.ts';

export type SocketioConnection = {
	namespace?: string;
	cookie_session_id?: string;
	requestAccessData?: boolean; // Asks the server to return extended from the initial dataset, i.e. access_policies, created and updated information.
};

export class SocketIO {
	// TBD: remove event and rooms from SocketioConnection
	// private connection: SocketioConnection;
	public client: Socket;

	constructor(connection: SocketioConnection) {
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
			query: { 'request-access-data': connection.requestAccessData || false }
		});
		this.client.connect();
	}

	// sendMessage(message: string) {
	//     this.socket.send(message);
	// }
	// sendMessage(message: string) {
	// 	console.log('Message sent:', message);
	// }
}

// import { io } from 'socket.io-client';

// let socketio_client: any;
// let new_message: string = '';
// let old_messages: string[] = [];

// implement check for localhost here
// socketio_client = io('http://localhost:8660');
// socketio_client.on('connect', () => {
//     console.log('=== socket opened ===');
//     socketio_client.send('Hello from the client!');
// });

// socketio_client.on('demo_message', (data: string) => {
//     console.log('Message from server:', data);
//     old_messages.push(data);
// });
// });

// const sendMessage = (event: Event) => {
// event.preventDefault();
// socketio_client.emit('demo_message', new_message);
