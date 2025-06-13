<script lang="ts">
	// import { onMount } from 'svelte';
	// import type { PageData } from './$types';
	// import { SocketIO } from '$lib/socketio';
	// import { io } from 'socket.io-client';
	import Heading from '$components/Heading.svelte';
	import Chat from './Chat.svelte';
	import type { SocketioConnection } from '$lib/socketio';
	import { page } from '$app/state';

	// const socketio_client_from_lib = new SocketIO();

	const public_message_connection: SocketioConnection = {
		namespace: '/public-namespace',
		room: '',
		cookie_session_id: page.data.session.sessionId
	};
	const demo_message_connection: SocketioConnection = {
		namespace: '/demo-namespace',
		room: '',
		cookie_session_id: page.data.session.sessionId
	};

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

<div class="m-5 grid grid-cols-2 gap-8">
	<div class="grow">
		<Chat connection={public_message_connection} socketioEvent="public_message"
			><Heading>Public Message Namespace</Heading></Chat
		>
	</div>
	<div>
		<Chat connection={demo_message_connection} socketioEvent="demo_message"
			><Heading>Demo Message Namespace</Heading></Chat
		>
	</div>
</div>

<!-- <div class="w-50">
=======
<Tabs {tabs}
	>Some Text - now changed. Put a Chat component here from $lib/chat, which is configures with the
	correct message</Tabs
>

<div class="w-50">
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

<Heading>Socket.IO message history</Heading>

{#each old_messages as old_message}
	<p>{old_message}</p>
{/each} -->
