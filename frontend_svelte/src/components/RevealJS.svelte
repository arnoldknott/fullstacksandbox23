<script lang="ts">
	import 'reveal.js/dist/reveal.css';
	import 'reveal.js/dist/theme/black.css';
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import Reveal from 'reveal.js';

	export const ssr = false;
	// let { children, keyboard=true }: {  children: Snippet, keyboard: boolean} = $props();
	let { children }: {  children: Snippet} = $props();

	onMount(() => {
		const reveal = new Reveal({});
		reveal.initialize({
			embeddded: true,
			keyboard: false,
			slideNumber: 'c/t',
			width: 1600,
			height: 900,
			margin: 0.01,
		});

	});
</script>

<div class="reveal">
	<div class="slides">
		{@render children?.()}
	</div>
</div>
