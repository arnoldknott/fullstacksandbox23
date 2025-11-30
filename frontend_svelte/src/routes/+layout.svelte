<script lang="ts">
	import '../app.css';
	import { setContext } from 'svelte';
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';

	let { children }: { children: Snippet } = $props();

	setContext('backendAPIConfiguration', page.data.backendAPIConfiguration);
</script>

<main class="h-screen overflow-y-hidden">
	{@render children?.()}
</main>
