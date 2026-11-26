<script lang="ts">
	import FormElement from '$components/FormElement.svelte';
	import FormMultipleSuffix from '$components/FormMultipleSuffix.svelte';
	import ShareItem from '$components/ShareItem.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import { isKebabCase } from '$lib/entities';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, NumberExtended } from '$lib/types';

	let {
		number,
		shareOptions,
		socketio,
		parentId,
		labelPending = $bindable(''),
		inheritPending = $bindable(false)
	}: {
		number: NumberExtended;
		shareOptions: AccessShareOption[];
		socketio: SocketIO<NumberExtended>;
		parentId?: string;
		labelPending?: string;
		inheritPending?: boolean;
	} = $props();

	const formId = $props.id();
	let suffix = $state('');
</script>

<div class="grid grid-cols-1 gap-x-6 lg:grid-cols-2">
	<div class="min-w-0">
		<FormElement title="Value" mandatory>
			<div class="input-filled input-primary w-full">
				<input
					id={`${formId}-value`}
					type="number"
					class="input"
					placeholder=""
					bind:value={number.value}
				/>
				<label class="input-filled-label" for={`${formId}-value`}>Value</label>
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
					bind:value={number.category}
					aria-invalid={Boolean(number.category) && !isKebabCase(number.category ?? '')}
				/>
				<label class="input-filled-label" for={`${formId}-category`}>Category</label>
			</div>
		</FormElement>
		{#if parentId}
			<FormElement title="Label">
				{#snippet description()}
					Optional label for this number under {parentId}. Use lowercase letters, digits and hyphens
					only; it must be unique among this parent's numbers.
				{/snippet}
				<div class="input-filled input-secondary w-full">
					<input
						id={`${formId}-label`}
						type="text"
						class="input"
						placeholder="number-label"
						bind:value={labelPending}
						aria-invalid={Boolean(labelPending) && !isKebabCase(labelPending)}
					/>
					<label class="input-filled-label" for={`${formId}-label`}>Label</label>
				</div>
			</FormElement>
		{/if}
	</div>
	<div class="min-w-0">
		<FormElement title="Access" extraClasses="max-w-130">
			{#snippet description()}
				Who has which access to this number? Default is public
				<span class="icon-[gis--globe-earth-alt] size-4"></span> and read
				<span
					class={`${AccessHandler.rightsIcon(Action.READ)} ${AccessHandler.rightsIconColor(Action.READ)} size-4`}
				></span>
				access.
			{/snippet}
			{#if parentId}
				<div class="label mb-2 flex flex-1 items-center gap-1">
					<label class="label label-text text-base-content" for="new-number-inherit">
						<input
							id="new-number-inherit"
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
						resourceId={number.id}
						shareOption={shareOptions[i]}
						{socketio}
						actions={[Action.OWN, Action.WRITE, Action.CONNECT, Action.READ, undefined]}
						wide
					/>
				{/each}
			</ul>
		</FormElement>

		<FormMultipleSuffix entityLabel="number" bind:suffix />
	</div>
</div>
