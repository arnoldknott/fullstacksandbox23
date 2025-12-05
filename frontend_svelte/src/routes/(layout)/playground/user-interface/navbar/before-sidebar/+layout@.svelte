<script lang="ts">
	import type { Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
</script>

<div data-theme="light">
	{@render children?.()}
</div>
{@render children?.()}
