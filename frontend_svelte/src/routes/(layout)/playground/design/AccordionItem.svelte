<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, children }: { title: string; children: Snippet } = $props();
	const id = title.toLowerCase().replaceAll(' ', '-');
</script>

<div class="active accordion-item bg-neutral-container text-neutral-container-content" {id}>
	<button
		class="accordion-toggle inline-flex items-center gap-x-4 text-start"
		aria-controls="{id}-collapse"
		aria-expanded="true"
	>
		<span
			class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
		></span>
		<p class="text-title md:text-title-large ml-10">{title}</p>
	</button>
	<div
		id="{id}-collapse"
		class="accordion-content w-full overflow-scroll transition-[height] duration-300 bg-neutral text-neutral-content"
		aria-labelledby={id}
		role="region"
	>
		{@render children?.()}
	</div>
</div>
