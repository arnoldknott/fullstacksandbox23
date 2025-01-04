<script lang="ts">
	import type { Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
	// console.log('=== lib - components - title - children ===');
	// console.log(children);
</script>

<div class="mx-5">
	<h1 class="heading md:heading-large mx-5 mb-2 mt-0 text-center text-primary">
		{@render children?.()}
	</h1>
</div>
