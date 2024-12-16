<script lang="ts">
	import type { Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
	// console.log('=== lib - components - title - children ===');
	// console.log(children);
</script>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-center text-4xl font-bold leading-tight text-blue-600">
		{@render children?.()}
	</h1>
</div>
