<script lang="ts">
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

<form id="post-message" class="flex flex-col" onsubmit={sendMessage}>
	<div class="flex flex-row items-center gap-4">
		<div class="input-filled w-fit grow">
			<input
				type="input"
				placeholder="Type your message here"
				class="input input-lg w-full grow"
				id={connection.namespace + connection.event + connection.room}
				name="message"
				value={new_message}
				oninput={(e: Event) => (new_message = (e.target as HTMLInputElement).value)}
				onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && sendMessage(e)}
			/>
			<label
				class="input-filled-label"
				for={connection.namespace + connection.event + connection.room}>Message</label
			>
		</div>
		<button
			class="btn-secondary-container btn btn-circle btn-gradient"
			aria-label="Add Icon Button"
		>
			<span class="icon-[tabler--send-2]"></span>
		</button>
	</div>
</form>

<p>Socket.IO message history</p>

<ul>
	{#each old_messages as old_message, i (i)}
		<li>➡️ {old_message}</li>
	{/each}
</ul>
