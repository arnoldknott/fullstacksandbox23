<script lang="ts" generics="T extends AnyEntityExtended">
	import type { Snippet } from 'svelte';
	import { slide } from 'svelte/transition';

	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import Card from '$components/Card.svelte';
	import { AccessHandler } from '$lib/accessHandler';
	import { EntityType, isKebabCase } from '$lib/entities';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, AnyEntityExtended } from '$lib/types';

	import AddDataTabs from './AddDataTabs.svelte';

	let {
		socketio,
		entityType,
		entityId,
		parentId,
		labelPending = $bindable(''),
		inheritPending = $bindable(false),
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
		labelPending?: string;
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
	let validationError = $state('');

	const submit = () => {
		if (!entity) return;
		validationError = '';
		const targets = isNew && bulk ? [...socketio.pendingEntities] : [entity];
		const hasCategory = entityType === EntityType.TEXT || entityType === EntityType.NUMBER;
		if (
			hasCategory &&
			targets.some(
				(target) => 'category' in target && target.category && !isKebabCase(target.category)
			)
		) {
			validationError = 'Category must contain only lowercase letters, digits and hyphens.';
			return;
		}
		const label = isNew && parentId ? labelPending || undefined : undefined;
		if (label !== undefined && !isKebabCase(label)) {
			validationError = 'Label must contain only lowercase letters, digits and hyphens.';
			return;
		}
		if (label !== undefined && targets.length > 1) {
			validationError = 'Create one resource at a time when assigning a parent-specific label.';
			return;
		}
		if (hasCategory) {
			for (const target of targets) {
				if ('category' in target && target.category === '') target.category = null;
			}
		}
		beforeSubmit?.(entity);
		if (!isNew) {
			socketio.submitEntity(entity);
			return;
		}
		if (label !== undefined) socketio.submitEntity(entity, parentId, inheritPending, label);
		else if (bulk) socketio.submitBulk(parentId, inheritPending);
		else socketio.submitEntity(entity, parentId, inheritPending);
		// Bulk and explicit submits do not refill the pending entities:
		socketio.createPending();
		labelPending = '';
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
			{#if validationError}
				<p class="label text-error mb-2" role="alert">{validationError}</p>
			{/if}
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
