<script lang="ts">
	import 'reveal.js/dist/reveal.css';
	import 'reveal.js/dist/theme/black.css';
	import { onMount } from 'svelte';
	import Reveal from 'reveal.js';

	export const ssr = false;
	let { children } = $props();

	onMount(() => {
		const reveal = new Reveal({});
		reveal.initialize({ embeddded: true, center: true, width: 1024, height: 768 });
	});
</script>

<div class="reveal">
	<div class="slides">
		{@render children?.()}
	</div>
</div>
