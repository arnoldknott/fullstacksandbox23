<script lang="ts">
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	import { SocketIO } from '$lib/socketio';
	import type { SocketioConnection } from '$lib/types';
	// import { getContext, type Snippet } from 'svelte';
	import { type Snippet } from 'svelte';

	let { connection, children }: { connection: SocketioConnection; children: Snippet } = $props();

	const socketio = new SocketIO(connection);

	let status = $state(false);
	$effect(() => {
		const updateStatus = () => {
			status = socketio.client.connected ? true : false;
			// console.log(`socketio status: ${status}`);
		};

		socketio.client.on('connect', updateStatus);
		socketio.client.on('disconnect', updateStatus);
		socketio.client.on(connection.event, updateStatus);
		updateStatus();
	});

	let new_message = $state('');

	let old_messages: string[] = $state([]);

	// TBD: add as method to SocketIO class
	const sendMessage = (event: Event) => {
		event.preventDefault();
		socketio.client.emit(connection.event, new_message);
		new_message = '';
	};

	$effect(() => {
		socketio.client.on(connection.event, (data) => {
			// console.log(`Received from socket.io server: ${data}`);
			old_messages.push(`${data}`);
		});
	});
</script>

{@render children?.()} in Chat / Connection
<span class={`icon-[openmoji--${status ? 'check-mark' : 'cross-mark'}] size-4`}></span>

<div class="w-50">
	<form id="post-message" class="flex flex-col" onsubmit={sendMessage}>
		<md-filled-text-field
			label="Message"
			type="input"
			name="message"
			role="textbox"
			tabindex="0"
			value={new_message}
			oninput={(e: Event) => (new_message = (e.target as HTMLInputElement).value)}
			onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && sendMessage(e)}
			class="w-50"
		>
		</md-filled-text-field>
		<div class="ml-auto py-4">
			<md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button>
		</div>
	</form>
</div>

<p>Socket.IO message history</p>

<ul>
	<!-- TBD: change key to id of message! -->
	{#each old_messages as old_message (old_message)}
		<li>➡️ {old_message}</li>
	{/each}
</ul>
