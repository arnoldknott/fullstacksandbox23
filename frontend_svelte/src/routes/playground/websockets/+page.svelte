<script lang="ts">
	import { onMount } from 'svelte';
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	import Title from '$components/Title.svelte';

	let new_message = $state('');
	let socket: WebSocket | undefined = $state(undefined);
	let old_messages: string[] = $state([]);

	onMount(async () => {
		socket = new WebSocket('ws://localhost:8660/ws/v1/public_web_socket');

		socket.onopen = (event) => {
			console.log('== socket opened ===');
			socket.send('Hello from the client!');
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
			console.log('=== socket closed ===');
		};
	});
</script>

<!-- TBD: clear text box -->
<div class="w-50">
	<form id="post-message" class="flex flex-col">
		<md-filled-text-field
			label="Message"
			type="input"
			name="message"
			oninput={(e) => (new_message = e.target.value)}
			class="w-50"
		>
		</md-filled-text-field>
		<div class="ml-auto py-4">
			<md-filled-button
				type="submit"
				role="button"
				onclick={socket?.send(new_message)}
				onkeydown={(e) => e.key === 'Enter' && socket?.send(new_message)}
				tabindex="0">OK</md-filled-button
			>
		</div>
	</form>
</div>

{#each old_messages as old_message}
	<Title>{old_message}</Title>
{/each}
