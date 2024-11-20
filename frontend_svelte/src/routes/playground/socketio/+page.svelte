<script lang="ts">
	// import { onMount } from 'svelte';
	// import type { PageData } from './$types';
	// import { SocketIO } from '$lib/socketio';
	// import { io } from 'socket.io-client';
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	// import Title from '$components/Title.svelte';
	import Tabs from '$components/Tabs.svelte';
	// import Chat from '$components/Chat.svelte';
	import type { Tab } from '$lib/types';

	// const socketio_client_from_lib = new SocketIO();

	const socketio_demo_message_connection = {
		event: 'demo_message',
		namespace: '',
		room: ''
	};
	const socketio_protected_message_connection = {
		event: 'protected_message',
		namespace: '',
		room: ''
	};

	const tabs: Tab[] = [
		{
			header: 'Demo Message',
			content: 'Demo message interface.',
			connection: socketio_demo_message_connection
		},
		{
			header: 'Protected Message',
			content: 'Protected message interface',
			connection: socketio_protected_message_connection,
			active: true
		}
	];

	// let { data }: { data: PageData } = $props();
	// const backend_fqdn = data.backend_fqdn;

	// const socketio_client = io('http://localhost:8660', { path: '/socketio/v1/' });
	// const socketio_server_url = backend_fqdn? `https://${backend_fqdn}` : 'http://localhost:8660';
	// const socketio_server_url = backend_fqdn.startsWith('localhost') ? `http://${backend_fqdn}` : `https://${backend_fqdn}`;
	// const socketio_client = io(socketio_server_url, { path: '/socketio/v1' });

	// let new_message = $state('');
	// let old_messages: string[] = $state([]);

	// Using Svelte5 runes for reactivity:
	// const message = $derived(socketio_client.emit("demo_message", "Hello from the client!"));
	// console.log('Message from client:', message);

	// // Adds a callback to be invoked when the derived value changes.
	// const message_with_acknowledge = $derived(socketio_client.emit("demo_message", "Hello from the client!", (message: string) => {
	// 	console.log('Message in callback function:', message);
	// 	old_messages.push(message);
	// }));
	// console.log('Message from client with callback:', message_with_acknowledge);

	// socketio_client.on('connect', () => {
	// 	console.log('=== socket opened ===');
	// 	socketio_client.send('Hello from the client!');
	// });

	// socketio_client.on('demo_message', (data) => {
	// 	console.log('Message from server:', data);
	// 	old_messages.push(data);
	// });

	// const sendMessage = (event: Event) => {
	// 	event.preventDefault();
	// 	socketio_client.emit('demo_message', new_message);
	// 	new_message = '';
	// };

	// socketio_client.on('demo_message', (data) => {
	// 	// console.log('Message from server:', data);
	// 	old_messages.push(data);
	// });

	// onMount(async () => {
	// 	socket = new WebSocket('ws://localhost:8660/ws/v1/public_web_socket');

	// 	socket.onopen = (event) => {
	// 		console.log('=== socket opened ===');
	// 		console.log('=== event ===');
	// 		console.log(event);
	// 		console.log('=== socket ===');
	// 		console.log(socket);
	// 		socket?.send('Hello from the client!');
	// 	};

	// 	// const sendMessage = (event) => {
	// 	//     event.preventDefault();
	// 	//     socket.send(message);

	// 	// };
	// 	socket.onmessage = (event) => {
	// 		console.log('Message from server:', event.data);
	// 		old_messages.push(event.data);
	// 	};
	// 	socket.onclose = (event) => {
	// 		console.log('=== socket closed ===');
	// 		console.log('=== event ===');
	// 		console.log(event);
	// 	};
	// });

	// const sendMessage = (event: Event) => {
	// 	event.preventDefault();
	// 	socket?.send(new_message);
	// };
</script>

<Tabs {tabs}>Some Text common to all tabs</Tabs>

<!-- <div class="w-50">
	<form id="post-message" class="flex flex-col" onsubmit={sendMessage}>
		<md-filled-text-field
			label="Message"
			type="input"
			name="message"
			value={new_message}
			oninput={(e: Event) => (new_message = (e.target as HTMLInputElement).value)}
			class="w-50"
		>
		</md-filled-text-field>
		<div class="ml-auto py-4">
			<md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button>
		</div>
	</form>
</div>

<Title>Socket.IO message history</Title>

{#each old_messages as old_message}
	<p>{old_message}</p>
{/each} -->
