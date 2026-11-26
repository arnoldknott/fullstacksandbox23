<script lang="ts">
	import FormElement from '$components/FormElement.svelte';
	import FormMultipleSuffix from '$components/FormMultipleSuffix.svelte';
	import ShareItem from '$components/ShareItem.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import { isKebabCase } from '$lib/entities';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, TextExtended } from '$lib/types';

	let {
		text,
		shareOptions,
		socketio,
		parentId,
		labelPending = $bindable(''),
		inheritPending = $bindable(false)
	}: {
		text: TextExtended;
		shareOptions: AccessShareOption[];
		socketio: SocketIO<TextExtended>;
		parentId?: string;
		labelPending?: string;
		inheritPending?: boolean;
	} = $props();

	const formId = $props.id();
	let suffix = $state('');
</script>

<div class="grid grid-cols-1 gap-x-6 lg:grid-cols-2">
	<div class="min-w-0">
		<FormElement title="Content" mandatory>
			<div class="textarea-filled textarea-primary w-full">
				<textarea
					id={`${formId}-content`}
					class="textarea"
					rows="6"
					placeholder="Add text content"
					bind:value={text.content}></textarea>
				<label class="textarea-filled-label" for={`${formId}-content`}>Content</label>
			</div>
		</FormElement>

		<FormElement title="Category">
			{#snippet description()}
				Optional. Use lowercase letters, digits and hyphens only.
			{/snippet}
			<div class="input-filled input-secondary w-full">
				<input
					id={`${formId}-category`}
					type="text"
					class="input"
					placeholder="category-name"
					bind:value={text.category}
					aria-invalid={Boolean(text.category) && !isKebabCase(text.category ?? '')}
				/>
				<label class="input-filled-label" for={`${formId}-category`}>Category</label>
			</div>
		</FormElement>

		{#if parentId}
			<FormElement title="Label">
				{#snippet description()}
					Optional label for this text under {parentId}. Use lowercase letters, digits and hyphens
					only; it must be unique among this parent's texts.
				{/snippet}
				<div class="input-filled input-secondary w-full">
					<input
						id={`${formId}-label`}
						type="text"
						class="input"
						placeholder="text-label"
						bind:value={labelPending}
						aria-invalid={Boolean(labelPending) && !isKebabCase(labelPending)}
					/>
					<label class="input-filled-label" for={`${formId}-label`}>Label</label>
				</div>
			</FormElement>
		{/if}

		<FormElement title="Confidential">
			{#snippet description()}
				This optional value is encrypted at rest.
			{/snippet}
			<div class="textarea-filled textarea-secondary w-full">
				<textarea
					id={`${formId}-confidential`}
					class="textarea"
					rows="3"
					placeholder="Confidential text"
					bind:value={text.confidential}></textarea>
				<label class="textarea-filled-label" for={`${formId}-confidential`}>Confidential</label>
			</div>
		</FormElement>
	</div>
	<div class="min-w-0">
		<FormElement title="Language" extraClasses="max-w-300">
			<div class="label">
				<span class="icon-[fluent-color--warning-24] size-4"></span>
				Language selection is not implemented yet. New texts default to English.
			</div>
		</FormElement>

		<FormElement title="Access" extraClasses="max-w-130">
			{#snippet description()}
				Who has which access to this text? Default is public
				<span class="icon-[gis--globe-earth-alt] size-4"></span> and read
				<span
					class={`${AccessHandler.rightsIcon(Action.READ)} ${AccessHandler.rightsIconColor(Action.READ)} size-4`}
				></span>
				access.
			{/snippet}
			{#if parentId}
				<div class="label mb-2 flex flex-1 items-center gap-1">
					<label class="label label-text text-base-content" for="new-text-inherit">
						<input
							id="new-text-inherit"
							type="checkbox"
							class="checkbox checkbox-primary"
							bind:checked={inheritPending}
						/>
					</label>
					inherit from {parentId}
				</div>
			{/if}
			<ul class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg p-2 shadow-inner">
				{#each shareOptions, i (i)}
					<ShareItem
						resourceId={text.id}
						shareOption={shareOptions[i]}
						{socketio}
						actions={[Action.OWN, Action.WRITE, Action.CONNECT, Action.READ, undefined]}
						wide
					/>
				{/each}
			</ul>
		</FormElement>

		<FormMultipleSuffix entityLabel="text" bind:suffix />
	</div>
</div>
