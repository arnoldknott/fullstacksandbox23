<script lang="ts">
	import RevealJs from '$components/RevealJS.svelte';
	import type { Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
</script>

<div class="h-screen w-screen">
	<RevealJs>
		{@render children?.()}
	</RevealJs>
</div>
