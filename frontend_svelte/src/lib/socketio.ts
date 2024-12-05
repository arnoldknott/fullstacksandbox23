// import { getContext } from 'svelte';
import { io } from 'socket.io-client';
import type { Socket } from 'socket.io-client';
import type { BackendAPIConfiguration } from '$lib/types.d.ts';
import type { SocketioConnection } from '$lib/types.d.ts';
// import { page } from '$app/stores';
export const ssr = false;

export class SocketIO {
	// TBD: remove event and rooms from SockerioConnection
	// private connection: SocketioConnection;
	public client: Socket;

	constructor(backendAPIConfiguration: BackendAPIConfiguration, connection: SocketioConnection) {
		// const backendAPIConfiguration: BackendAPIConfiguration = getContext('backendAPIConfiguration');
		// // this.connection = connection;
		// let backendAPIConfiguration
		// const unsubscribePageData = page.subscribe((value) => backendAPIConfiguration = value);
		// console.log('=== SocketIO constructor - backendAPIConfiguration ===');
		// console.log(backendAPIConfiguration);
		// $effect(() => {
		// if (backendAPIConfiguration && backendAPIConfiguration?.backendFqdn) {
		// console.log('=== SocketIO constructor - backendAPIConfiguration ===');
		// console.log(backendAPIConfiguration.backendFqdn);

		const backendFqdn = backendAPIConfiguration.backendFqdn;
		const socketioServerUrl = backendFqdn.startsWith('localhost')
			? `http://${backendFqdn}`
			: `https://${backendFqdn}`;
		this.client = io(socketioServerUrl + connection.namespace, { path: `/socketio/v1` });
		this.client.connect();

		// } else {
		// 	console.error('=== SocketIO constructor - backendAPIConfiguration not set ===');
		// }
		// })
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
