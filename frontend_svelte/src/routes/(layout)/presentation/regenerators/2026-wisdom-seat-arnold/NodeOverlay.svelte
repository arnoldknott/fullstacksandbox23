<script lang="ts">
	import type { Snippet } from 'svelte';

	import CardOverlay from './CardOverlay.svelte';
	import NodeButton from './NodeButton.svelte';

	let {
		buttonText,
		defaultButton = true,
		buttonExtraClasses,
		cardExtraClasses,
		children
	}: {
		buttonText: Snippet;
		defaultButton?: boolean;
		buttonExtraClasses?: string;
		cardExtraClasses?: string;
		children: Snippet;
	} = $props();
	let hidden = $state(true);
</script>

<NodeButton standard={defaultButton} class={buttonExtraClasses} bind:toggleVariable={hidden}
	>{@render buttonText()}</NodeButton
>

<CardOverlay class="z-50 pt-6  {cardExtraClasses}" bind:hidden>
	{@render children()}
</CardOverlay>
