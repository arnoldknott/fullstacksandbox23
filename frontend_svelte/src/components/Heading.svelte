<script lang="ts">
	import { onDestroy, onMount, type Snippet } from 'svelte';
	import type { HTMLAttributes } from 'svelte/elements';

	import { getOnThisPageLinks } from '$lib/contexts/sidebar.svelte';
	let {
		children,
		id,
		sideBarEntry,
		...rest
	}: { children: Snippet; id: string; sideBarEntry?: string } & HTMLAttributes<HTMLElement> =
		$props();

	const onThisPageLinks = getOnThisPageLinks();

	/*
	TBD: consider also adding the Display component to the side bar (as folders),
	Then Headings can be inside those folders
	Also consider removing those items from the global side bar!
	*/
	onMount(() => {
		if (sideBarEntry) {
			onThisPageLinks.push({
				id: `on-this-page-${id}`,
				name: sideBarEntry,
				icon: 'icon-[tabler--chevrons-right]',
				hash: '#' + id
			});
		}
	});
	onDestroy(() => {
		const index = onThisPageLinks.findIndex((item) => item.id === `on-this-page-${id}`);
		if (index >= 0) onThisPageLinks.splice(index, 1);
	});
	// let props = $props();
	// console.log('=== lib - components - title - children ===');
	// console.log(children);
</script>

<!-- decide weather to use text-base-content or text-primary -->

<div {...rest} class="mt-20 flex flex-row {rest.class ?? ''}">
	<a href={'#' + id} class="self-center" aria-label="Link to this section">
		<span
			class="icon-[tabler--link] text-secondary/30 hover:text-secondary/80 mr-2 size-4 self-center md:size-6 lg:size-7"
		></span>
	</a>
	<h2 {id} class="heading-small md:heading lg:heading-large text-primary mt-0 tracking-wider">
		{@render children?.()}
	</h2>
	<!-- TBD: Consider adding a label/subheading underneath: -->
	<!-- <p class="label text-base-content-variant">{subheading}</p> -->
</div>
