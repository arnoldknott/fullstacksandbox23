<script lang="ts">
	import type { PageData } from './$types';
	import { onMount } from 'svelte';
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	import Heading from '$components/Heading.svelte';

	let { data }: { data: PageData } = $props();
	const backend_fqdn = data.backend_fqdn;
	console.log('=== playground - backend_fqdn ===');
	console.log(backend_fqdn);

	let new_message = $state('');
	let socket: WebSocket | undefined = $state(undefined);
	let old_messages: string[] = $state([]);

	onMount(async () => {
		// socket = new WebSocket('ws://localhost:8660/ws/v1/public_web_socket');
		// implement check for localhost here
		const websocket_server_url = backend_fqdn.startsWith('localhost')
			? `ws://${backend_fqdn}/ws/v1/public_web_socket`
			: `wss://${backend_fqdn}/ws/v1/public_web_socket`;
		socket = new WebSocket(websocket_server_url);

		socket.onopen = (event) => {
			console.log('=== playground - websocket opened ===');
			console.log('=== event ===');
			console.log(event);
			// console.log('=== socket ===');
			// console.log(socket);
			socket?.send('Hello from the client!');
		};

		// const sendMessage = (event) => {
		//     event.preventDefault();
		//     socket.send(message);

		// };
		socket.onmessage = (event) => {
			console.log('Message from server:', event.data);
			old_messages.push(event.data);
		};

		socket.onclose = (event) => {
			console.log('=== playground - socket closed ===');
			console.log('=== event ===');
			console.log(event);
		};
	});

	const sendMessage = (event: Event) => {
		event.preventDefault();
		socket?.send(new_message);
	};
</script>

<!-- TBD: clear text box -->
<div class="w-50">
	<form id="post-message" class="flex flex-col" onsubmit={sendMessage}>
		<md-filled-text-field
			label="Message"
			type="input"
			name="message"
			oninput={(e: Event) => (new_message = (e.target as HTMLInputElement).value)}
			class="w-50"
		>
		</md-filled-text-field>
		<div class="ml-auto py-4">
			<md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button>
		</div>
	</form>
</div>

<!-- TBD: change key to unique value -->
{#each old_messages as old_message (old_message)}
	<Heading>{old_message}</Heading>
{/each}
