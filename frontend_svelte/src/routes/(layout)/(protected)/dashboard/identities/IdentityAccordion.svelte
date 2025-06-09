<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, id, children }: { title: string; id: string; children: Snippet } = $props();

	// export interface MicrosoftTeamBasic {
	// 	id: string;
	// 	displayName: string;
	// 	description: string;
	// }
</script>

<div class="accordion-item bg-neutral-container text-neutral-container-content" {id}>
	<button
		class="accordion-toggle inline-flex items-center gap-x-4 text-start"
		aria-controls="{id}-collapse"
		aria-expanded="false"
	>
		<span
			class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
		></span>
		<p class="title md:title-large ml-10">{title}</p>
	</button>
	<div
		id="{id}-collapse"
		class="accordion-content bg-neutral text-neutral-content hidden w-full overflow-scroll p-4 transition-[height] duration-300"
		aria-labelledby={id}
		role="region"
	>
		{@render children?.()}
	</div>
</div>
