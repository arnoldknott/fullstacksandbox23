<script lang="ts">
	import type { Snippet } from 'svelte';

	import type { EntityType } from '$lib/entityContainer.svelte';
	import { initTabs } from '$lib/userInterface';

	let {
		entityType,
		children,
		existing
	}: {
		entityType: EntityType;
		children: Snippet;
		existing?: Snippet;
	} = $props();
</script>

{#snippet warning()}
	<span class="icon-[fluent-color--warning-24] size-4"></span>
{/snippet}

<div class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg shadow-inner">
	<div
		class="tabs tabs-lifted tabs-secondary m-0!"
		// class="tabs tabs-lifted to-secondary m-1 rounded-lg bg-linear-to-b from-transparent"
		// class="tabs tabs-lifted to-secondary m-1 bg-linear-to-b from-transparent"
		aria-label="Tabs"
		role="tablist"
		aria-orientation="horizontal"
		{@attach initTabs}
	>
		<button
			type="button"
			// class="tab tab-secondary active w-full"
			class="tab active w-full"
			id={`new-${entityType}-head`}
			data-tab={`#new-${entityType}-tab`}
			aria-controls={`new-${entityType}-tab`}
			role="tab"
			aria-selected="true"
		>
			<span class="icon-[fa6-solid--plus] mr-2 size-4"></span>
			<span class="hidden md:inline">Add</span>
			<span class="hidden sm:inline">&nbsp;new</span>
		</button>
		<button
			type="button"
			// class="tab tab-secondary w-full"
			class="tab w-full"
			id={`existing-${entityType}-head`}
			data-tab={`#existing-${entityType}-tab`}
			aria-controls={`existing-${entityType}-tab`}
			role="tab"
			aria-selected="false"
		>
			<span class="icon-[tabler--copy] mr-2 size-4"></span>
			<span class="hidden md:inline">Copy </span>
			&nbsp;or&nbsp;
			<span class="icon-[tabler--link] mx-2 size-4"></span>
			<span class="hidden md:inline">link </span>
			<span class="hidden sm:inline">&nbsp;existing</span>
		</button>
	</div>
	<div class="h-fit p-2">
		<div
			id={`new-${entityType}-tab`}
			class="h-full max-h-120 overflow-scroll"
			role="tabpanel"
			aria-labelledby={`new-${entityType}-head`}
		>
			{@render children()}
		</div>
		<div
			id={`existing-${entityType}-tab`}
			class="hidden h-full max-h-100 overflow-scroll"
			role="tabpanel"
			aria-labelledby={`existing-${entityType}-head`}
		>
			<div class="label">
				{@render warning()} Table of existing {entityType}s and functionality to link or copy them
				into the parent.
			</div>
			{@render existing?.()}
		</div>
	</div>
</div>
