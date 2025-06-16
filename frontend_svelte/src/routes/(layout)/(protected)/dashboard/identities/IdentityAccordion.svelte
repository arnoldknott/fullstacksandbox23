<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, id, open = true, children }: { title: string; id: string; open?: boolean; children: Snippet } = $props();

	// export interface MicrosoftTeamBasic {
	// 	id: string;
	// 	displayName: string;
	// 	description: string;
	// }
</script>

<div class="accordion-item bg-neutral-container text-neutral-container-content {open ? 'active' : ''}" {id}>
	<button
		class="accordion-toggle inline-flex items-center gap-x-4 text-start"
		aria-controls="{id}-collapse"
		aria-expanded={open}
	>
		<span
			class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
		></span>
		<p class="title ml-10">{title}</p>
	</button>
	<div
		id="{id}-collapse"
		class="accordion-content bg-base-200 text-base-content-variant {!open ? 'hidden' : ''} w-full overflow-scroll p-4 transition-[height] duration-300"
		aria-labelledby={id}
		role="region"
	>
		{@render children?.()}
	</div>
</div>
