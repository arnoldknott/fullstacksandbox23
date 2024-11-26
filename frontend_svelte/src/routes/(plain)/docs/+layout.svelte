<script lang="ts">
	import RevealJs from '$components/RevealJS.svelte';
	import type { Snippet } from 'svelte';
	// let { keyboard, children }: { keyboard: boolean, children: Snippet } = $props();
	let { keyboard, children }: { keyboard: boolean; children: Snippet } = $props();

	// let keyboard = $state(true);
	// console.log("=== docs - layout.svelte - keyboard ===");
	// console.log(keyboard);
</script>

<div class="h-screen w-screen">
	<RevealJs {keyboard}>
		{@render children?.()}
	</RevealJs>
</div>
