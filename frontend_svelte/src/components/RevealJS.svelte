<script lang="ts">
	import 'reveal.js/dist/reveal.css';
	import 'reveal.js/dist/theme/black.css';
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import Reveal from 'reveal.js';
	import type {Options } from 'reveal.js';
	type RevealType = typeof Reveal;

	export const ssr = false;
	// let { children, keyboard=true }: {  children: Snippet, keyboard: boolean} = $props();
	let { children, options = {}, reveal = $bindable() }: { children: Snippet; options?: Options; reveal?: RevealType } = $props();

	

	onMount(() => {
		const reveal = new Reveal({});
		reveal.initialize({
			// Default options
			embedded: true,
			slideNumber: 'c/t',
			width: 1600,
			height: 900,
			margin: 0.01,
			// Override with external options
			...options
		});
		reveal.on('fragmentshown', (event) => {
			console.log('=== fragment shown ===');
			console.log(event);
		});
	});
</script>

<div class="reveal">
	<div class="slides">
		{@render children?.()}
	</div>
</div>
