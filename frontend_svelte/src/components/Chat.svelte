<script lang="ts">
    import '@material/web/textfield/filled-text-field.js';
    import '@material/web/button/filled-button.js';
    import Title from '$components/Title.svelte';

    import { SocketIO } from '$lib/socketio';

    const socketio_client = new SocketIO();
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

<Title>Socket.IO message history</Title>

{#each old_messages as old_message}
	<p>{old_message}</p>
{/each}