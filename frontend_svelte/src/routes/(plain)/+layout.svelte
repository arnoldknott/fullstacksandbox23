<script lang="ts">
	import '../../app.css';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<main data-theme="dark">
	{@render children?.()}
</main>
