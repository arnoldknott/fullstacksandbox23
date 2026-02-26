<script lang="ts">
	import type { Snippet } from 'svelte';
	let { children, color }: { children: Snippet; color?: string } = $props();
</script>

<div class="display-large font-semibold {color ? `text-${color}` : ''}">{@render children()}</div>
