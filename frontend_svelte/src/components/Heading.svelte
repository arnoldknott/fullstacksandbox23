<script lang="ts">
	import type { Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
	// console.log('=== lib - components - title - children ===');
	// console.log(children);
</script>

<div class="mx-5">
	<h1 class="heading-small md:heading lg:heading-large text-base-content mx-5 mt-0 mb-2 text-center">
		{@render children?.()}
	</h1>
</div>
