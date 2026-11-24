<script lang="ts">
	import { slide } from 'svelte/transition';

	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import Card from '$components/Card.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { PresentationExtended } from '$lib/types';

	import PresentationForm from './PresentationForm.svelte';

	let {
		socketio,
		presentationId = socketio.pendingEntities[0]?.id,
		hidden = $bindable()
	}: {
		socketio: SocketIO<PresentationExtended>;
		presentationId?: string;
		hidden: boolean;
	} = $props();

	let newPresentation = $derived(presentationId === socketio.pendingEntities[0]?.id);

	let presentation = $derived(
		newPresentation
			? socketio.pendingEntities[0]
			: socketio.entities.find((entity) => entity.id === presentationId)
	);

	const submitPresentation = () => {
		if (!presentation) return;
		const newPath = presentation.path?.trim() ?? '';
		presentation.path = newPath && !newPath.startsWith('/') ? `/${newPath}` : newPath;
		socketio.submitEntity(presentation);
		socketio.createPending();
		hidden = newPresentation;
	};
</script>

{#if presentation}
	<Card
		id={presentation.id}
		title={presentation.path ? presentation.path : 'New presentation'}
		closeButton={newPresentation}
		bind:hidden
	>
		<PresentationForm {presentation} {socketio} />
		{#snippet footer()}
			<div class="ml-5 flex flex-row justify-end gap-4">
				{#if newPresentation}
					<button
						class="btn btn-secondary-container btn-gradient shadow-outline rounded-full shadow"
						aria-label="Cancel"
						onclick={() => {
							hidden = true;
						}}><span class="icon-[tabler--x] size-5"></span>Cancel</button
					>
				{:else}
					<button
						class="btn btn-error-container btn-gradient bg-error-container/70 shadow-outline rounded-full shadow"
						aria-label="Delete"
						onclick={() => {
							socketio.deleteEntity(presentationId);
							goto(resolve('/(layout)/presentation/(protected)/setup'));
						}}><span class="icon-[tabler--trash] size-5"></span>Delete</button
					>
				{/if}
				<button
					class="btn btn-primary-container btn-gradient shadow-outline rounded-full shadow"
					aria-label="Save new presentation"
					onclick={() => submitPresentation()}
					><span class="icon-[tabler--send-2] size-5"></span>Save</button
				>
			</div>
		{/snippet}
	</Card>
{:else}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		No presentation data available.
	</div>
{/if}
