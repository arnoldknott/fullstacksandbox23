<script lang="ts" generics="T extends AnyEntityExtended">
	import type { Snippet } from 'svelte';
	import { slide } from 'svelte/transition';

	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import Card from '$components/Card.svelte';
	import { AccessHandler } from '$lib/accessHandler';
	import { EntityType } from '$lib/entityContainer.svelte';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, AnyEntityExtended } from '$lib/types';

	import AddDataTabs from './AddDataTabs.svelte';

	let {
		socketio,
		entityType,
		entityId,
		parentId,
		inheritPending = false,
		hidden = $bindable(false),
		title,
		beforeSubmit,
		form,
		existing
	}: {
		socketio: SocketIO<T>;
		entityType: EntityType;
		// Without entityId the card edits the pending (new) entity:
		entityId?: string;
		parentId?: string;
		inheritPending?: boolean;
		hidden?: boolean;
		title?: (entity: T) => string | undefined;
		beforeSubmit?: (entity: T) => void;
		form: Snippet<[T, AccessShareOption[]]>;
		existing?: Snippet;
	} = $props();

	let isNew = $derived(entityId === undefined);
	let entity = $derived(
		isNew
			? socketio?.pendingEntities[0]
			: socketio?.entities.find((candidate) => candidate.id === entityId)
	);
	let shareOptions: AccessShareOption[] = $derived(
		entity
			? AccessHandler.createShareOptions(socketio.identities, socketio.accessPolicies[entity.id]) ||
					[]
			: []
	);
	let bulk = $derived(entityType !== EntityType.PRESENTATION);

	const submit = () => {
		if (!entity) return;
		beforeSubmit?.(entity);
		if (!isNew) {
			socketio.submitEntity(entity);
			return;
		}
		if (bulk) socketio.submitBulk(parentId, inheritPending);
		else socketio.submitEntity(entity, parentId, inheritPending);
		// Bulk and explicit submits do not refill the pending entities:
		socketio.createPending();
		hidden = true;
	};

	const remove = () => {
		if (!entity) return;
		socketio.deleteEntity(entity.id);
		goto(resolve(`/(layout)/${entityType}/(protected)/setup`));
	};
</script>

{#if entity}
	<Card
		id={entity.id}
		title={title?.(entity) || (isNew ? `New ${entityType}` : entity.id)}
		closeButton={isNew}
		bind:hidden
	>
		{#if parentId}
			<AddDataTabs {entityType} {existing}>
				{@render form(entity, shareOptions)}
			</AddDataTabs>
		{:else}
			{@render form(entity, shareOptions)}
		{/if}
		{#snippet footer()}
			<div class="ml-5 flex flex-row justify-end gap-4">
				{#if isNew}
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
						onclick={remove}><span class="icon-[tabler--trash] size-5"></span>Delete</button
					>
				{/if}
				<button
					class="btn btn-primary-container btn-gradient shadow-outline rounded-full shadow"
					aria-label={`Save ${entityType}`}
					onclick={submit}><span class="icon-[tabler--send-2] size-5"></span>Save</button
				>
			</div>
		{/snippet}
	</Card>
{:else if !hidden}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		No {entityType} data available.
	</div>
{/if}
