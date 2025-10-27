<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';
	let { children, id, ...rest }: { children: Snippet; id: string } & HTMLAttributes<HTMLElement> =
		$props();
	// let props = $props();
</script>

<div {...rest} class={rest.class ?? ''}>
	<h3 {id} class="title lg:title-large text-accent">
		{@render children?.()}
	</h3>
</div>
