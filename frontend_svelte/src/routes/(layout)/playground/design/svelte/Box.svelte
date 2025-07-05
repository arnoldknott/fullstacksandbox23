<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, children }: { title: string; header?: Snippet; children: Snippet } = $props();
</script>

<div class="w-full">
	<div class="title-large text-center">{title}</div>

	<div class="bg-base-150 shadow-outline h-140 w-full rounded-lg p-2 shadow-inner">
		{@render children?.()}
	</div>
</div>
