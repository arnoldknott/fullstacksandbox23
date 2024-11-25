import { getContext } from 'svelte';
import { io } from 'socket.io-client';
import type { Socket } from 'socket.io-client';
import type { BackendAPIConfiguration } from '$lib/types.d.ts';
import type { SocketioConnection } from '$lib/types.d.ts';

export class SocketIO {
	private connection: SocketioConnection;
	public client: Socket;

	constructor(connection: SocketioConnection) {
		const backendAPIConfiguration: BackendAPIConfiguration = getContext('backendAPIConfiguration');
		this.connection = connection;
		const backendFqdn = backendAPIConfiguration.backendFqdn;
		const socketioServerUrl = backendFqdn.startsWith('localhost')
			? `http://${backendFqdn}`
			: `https://${backendFqdn}`;
		this.client = io(socketioServerUrl + connection.namespace, { path: `/socketio/v1` });
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