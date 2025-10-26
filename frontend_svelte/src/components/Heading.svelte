<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';
	let { children, ...rest }: { children: Snippet } & HTMLAttributes<HTMLElement> = $props();
	// let props = $props();
	// console.log('=== lib - components - title - children ===');
	// console.log(children);
</script>

<!-- decide weather to use text-base-content or text-primary -->

<div {...rest} class={rest.class ?? ''}>
	<h2 class="heading-small md:heading lg:heading-large text-secondary mt-0 mb-2">
		{@render children?.()}
	</h2>
</div>
