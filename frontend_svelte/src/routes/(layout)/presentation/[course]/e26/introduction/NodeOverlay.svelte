<script lang="ts">
	import type { Snippet } from 'svelte';

	import CardOverlay from './CardOverlay.svelte';
	import NodeButton from './NodeButton.svelte';

	let {
		buttonText,
		defaultButton = true,
		buttonExtraClasses,
		cardExtraClasses,
		header,
		children
	}: {
		buttonText: Snippet;
		defaultButton?: boolean;
		buttonExtraClasses?: string;
		cardExtraClasses?: string;
		header?: Snippet;
		children: Snippet;
	} = $props();
	let hidden = $state(true);
</script>

<NodeButton standard={defaultButton} class={buttonExtraClasses} bind:toggleVariable={hidden}
	>{@render buttonText()}</NodeButton
>

<CardOverlay class="z-50 pt-6 {cardExtraClasses}" bind:hidden {header}>
	{@render children()}
</CardOverlay>
