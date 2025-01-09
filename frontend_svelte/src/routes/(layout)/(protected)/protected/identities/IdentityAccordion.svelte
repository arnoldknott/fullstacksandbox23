<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, id, children }: { title: string; id: string; children: Snippet } = $props();

	export interface MicrosoftTeamBasicInformation {
		id: string;
		displayName: string;
		description: string;
	}
</script>

<div class="accordion-item" {id}>
	<button
		class="accordion-toggle inline-flex items-center gap-x-4 text-start"
		aria-controls="{id}-collapse"
		aria-expanded="false"
	>
		<span
			class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
		></span>
		<p class="text-title md:text-title-large ml-10">{title}</p>
	</button>
	<div
		id="{id}-collapse"
		class="accordion-content hidden w-full overflow-scroll p-4 transition-[height] duration-300"
		aria-labelledby={id}
		role="region"
	>
		{@render children?.()}
	</div>
</div>
