<script lang="ts">
	import type { Snippet } from 'svelte';
	let {
		title,
		active = true,
		children
	}: { title: string; active?: boolean; children: Snippet } = $props();
	const id = title.toLowerCase().replaceAll(' ', '-');
</script>

<div
	class="{active
		? 'active'
		: ''} accordion-item bg-neutral-container text-neutral-container-content"
	{id}
>
	<button
		class="accordion-toggle inline-flex items-center gap-x-4 text-start"
		aria-controls="{id}-collapse"
		aria-expanded={active}
	>
		<span
			class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
		></span>
		<p class="title md:title-large ml-10">{title}</p>
	</button>
	<div
		id="{id}-collapse"
		class="{!active
			? 'hidden'
			: ''} accordion-content bg-background text-base-content w-full overflow-scroll transition-[height] duration-300"
		aria-labelledby={id}
		role="region"
	>
		{@render children?.()}
	</div>
</div>
