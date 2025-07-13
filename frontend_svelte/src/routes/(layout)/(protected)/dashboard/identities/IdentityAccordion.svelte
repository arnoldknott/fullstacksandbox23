<script lang="ts">
	import type { Snippet } from 'svelte';
	import IdBadge from '../IdBadge.svelte';
	let {
		icon,
		title,
		id,
		open = true,
		children
	}: { icon?: string; title: string; id: string; open?: boolean; children: Snippet } = $props();

	// export interface MicrosoftTeamBasic {
	// 	id: string;
	// 	displayName: string;
	// 	description: string;
	// }
</script>

<div
	class="accordion-item bg-neutral-container text-neutral-container-content {open ? 'active' : ''}"
	{id}
>
	<div class="flex flex-col">
		<button
			class="accordion-toggle inline-flex items-center gap-x-4 text-start"
			aria-controls="{id}-collapse"
			aria-expanded={open}
		>
			<span
				class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 mr-10 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
			></span>
			{#if icon}
				<span class="{icon} shrink-0"></span>
			{/if}
			<div class="flex w-full flex-row">
				<p class="title grow">{title}</p>
				<IdBadge {id} />
			</div>
		</button>
		<div class="badge badge-secondary-container badge-sm mb-4 place-self-center md:hidden">
			{id}
		</div>
	</div>
	<div
		id="{id}-collapse"
		class="accordion-content bg-base-200 text-base-content-variant {!open
			? 'hidden'
			: ''} w-full overflow-scroll p-4 transition-[height] duration-300"
		aria-labelledby={id}
		role="region"
	>
		{@render children?.()}
	</div>
</div>
