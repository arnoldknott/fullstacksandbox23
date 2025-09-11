<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';
	let { children, ...rest }: { children: Snippet } & HTMLAttributes<HTMLElement> = $props();
	// let props = $props();
	// console.log('=== lib - components - title - children ===');
	// console.log(children);
</script>

<!-- <div id={props.id} class="{props.class} mx-5 text-green-500">
	<h1
		class="heading-small md:heading lg:heading-large text-base-content mx-5 mb-2 mt-0 text-center"
	>
		{@render props.children?.()}
	</h1>
	<p>blabla {props.class}</p>
</div> -->

<div {...rest} class="mx-5 {rest.class ?? ''}">
	<h1
		class="heading-small md:heading lg:heading-large text-base-content mx-5 mb-2 mt-0 text-center"
	>
		{@render children?.()}
	</h1>
</div>
