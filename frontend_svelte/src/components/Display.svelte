<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';
	let { children, ...rest }: { children: Snippet} & HTMLAttributes<HTMLElement> = $props();
	// let props = $props();
</script>

<div {...rest} class="mx-5 {rest.class ?? ''}">
	<h1
		class="display-small lg:display text-primary mx-5 mt-0 mb-2 text-center"
	>
		{@render children?.()}
	</h1>
</div>
