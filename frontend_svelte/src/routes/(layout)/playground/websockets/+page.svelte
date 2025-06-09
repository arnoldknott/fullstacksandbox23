<script lang="ts">
	import type { PageData } from './$types';
	import { onMount } from 'svelte';
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
		new_message = '';
	};
</script>

<form id="post-message" class="flex flex-col" onsubmit={sendMessage}>
	<div class="flex flex-row items-center gap-4">
		<div class="input-filled w-fit grow">
			<input
				type="input"
				placeholder="Type your message here"
				class="input input-lg w-full grow"
				id="websocketTest"
				name="message"
				value={new_message}
				oninput={(e: Event) => (new_message = (e.target as HTMLInputElement).value)}
			/>
			<label class="input-filled-label" for="websocketTest">Message</label>
		</div>
		<button
			class="btn-secondary-container btn btn-circle btn-gradient"
			aria-label="Add Icon Button"
		>
			<span class="icon-[tabler--send-2]"></span>
		</button>
	</div>
</form>

{#each old_messages as old_message, i (i)}
	<Heading>{old_message}</Heading>
{/each}
