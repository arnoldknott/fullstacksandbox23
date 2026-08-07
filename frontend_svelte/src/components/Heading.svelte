<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLAttributes } from 'svelte/elements';
	let { children, id, ...rest }: { children: Snippet; id: string } & HTMLAttributes<HTMLElement> =
		$props();
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
