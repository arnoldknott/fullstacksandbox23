<script lang="ts">
	import { type Snippet } from 'svelte';
	let {
		id,
		// header,
		children
	}: {
		id: string;
		// header?: Snippet;
		children: Snippet;
	} = $props();
</script>

<div {id}>
	<!-- {@render header?.()} -->
	{@render children?.()}
</div>
