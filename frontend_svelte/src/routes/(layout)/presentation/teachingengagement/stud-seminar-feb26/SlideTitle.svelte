<script lang="ts">
	import type { Snippet } from 'svelte';
	let { color = 'secondary', children }: { color?: string; children: Snippet } = $props();
</script>

<div class="w-full flex-shrink-0 px-2 pt-1 pb-2">
	<div class={`text-${color} text-center text-6xl font-bold`}>
		{@render children()}
	</div>
</div>
