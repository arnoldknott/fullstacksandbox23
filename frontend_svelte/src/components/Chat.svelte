<script lang="ts">
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	import Title from '$components/Title.svelte';
	import { SocketIO } from '$lib/socketio';
	import type { SocketioConnection } from '$lib/types';
	import type { Snippet } from 'svelte';

	let { connection, children }: { connection: SocketioConnection; children: Snippet } = $props();

	const socketio = new SocketIO(connection);
	let new_message = $state('');

	let old_messages: string[] = $state([]);

	const sendMessage = (event: Event) => {
		event.preventDefault();
		socketio.client.emit(connection.event, new_message);
		new_message = '';
	};

	$effect(() => {
		socketio.client.on(connection.event, (data) => {
			console.log(`Response from server: ${data}`);
			old_messages.push(`Response from server: ${data}`);
		});
	});
</script>

<p>{@render children?.()} in Chat</p>

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

<p>Socket.IO message history</p>

{#each old_messages as old_message}
	<Title>{old_message}</Title>
{/each}
