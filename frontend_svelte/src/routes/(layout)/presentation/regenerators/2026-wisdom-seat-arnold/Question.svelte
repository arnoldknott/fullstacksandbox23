<script lang="ts">
	import type { Snippet } from 'svelte';

	import Badge from './Badge.svelte';
	let {
		title,
		children,
		color = 'secondary'
	}: { title: string; children: Snippet; color?: string } = $props();
</script>

<div
	class="text-secondary-content bg-secondary shadow-base-shadow shadow-large rounded-full p-6 px-40 text-7xl font-semibold shadow-inner"
>
	<Badge {title} {color} />
	<div class="mt-4">
		{@render children()}
	</div>
</div>
