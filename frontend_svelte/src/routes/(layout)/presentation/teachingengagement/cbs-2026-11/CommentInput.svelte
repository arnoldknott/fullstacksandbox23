<script lang="ts">
	import Icon from '@iconify/svelte';

	import { Action } from '$lib/accessHandler';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

	import NameInput from './NameInput.svelte';

	let {
		socketio,
		parentId,
		bookId,
		name = $bindable(''),
		text = $bindable(''),
		label = 'Do you have comments or questions?',
		onsubmit
	}: {
		socketio?: SocketIO<MessageExtended>;
		parentId?: string;
		bookId?: string;
		name?: string;
		text?: string;
		label?: string;
		onsubmit?: () => void;
	} = $props();
	const inputId = $props.id();
	let submissionParentId = $derived(parentId ?? socketio?.parentId);

	const submit = () => {
		const pending = socketio?.pendingEntities[0];
		if (!socketio || !pending || !submissionParentId || !text.trim()) return;
		pending.content = bookId ? JSON.stringify({ bookdid: bookId, comment: text }) : text;
		pending.confidential = name.trim() || 'Anonymous';
		socketio.addPendingAccessPolicy(pending.id, { public: true, action: Action.READ });
		socketio.submitEntity(pending, submissionParentId, true);
		socketio.createPending();
		text = '';
		onsubmit?.();
	};
</script>

<form
	class="grid min-w-0 gap-4 text-left"
	onsubmit={(event) => {
		event.preventDefault();
		submit();
	}}
>
	<NameInput bind:name />
	<div class="textarea-filled textarea-base-content w-full">
		<textarea
			class="textarea min-h-32"
			placeholder=""
			id={inputId}
			required
			bind:value={text}
			onkeydown={(event) => {
				if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
					event.preventDefault();
					submit();
				}
			}}></textarea>
		<label class="textarea-filled-label" for={inputId}>{label}</label>
	</div>
	<div class="text-right">
		<button
			type="submit"
			class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
			disabled={!socketio?.pendingEntities[0] || !submissionParentId || !text.trim()}
		>
			<Icon icon="tabler:send" class="size-5" />Send
		</button>
	</div>
</form>
