<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';
	let { children, ...rest }: { children: Snippet } & HTMLAttributes<HTMLElement> = $props();
	// let props = $props();
</script>

<div {...rest} class={rest.class ?? ''}>
	<h1 class="display-small lg:display text-primary mt-0 mb-2 text-center">
		{@render children?.()}
	</h1>
</div>
