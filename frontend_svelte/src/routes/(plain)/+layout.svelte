<script lang="ts">
	import '../../app.css';
	// import { setContext } from 'svelte';
	// import type { LayoutData } from '../$types';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
	// let data: LayoutData = $props();
	// console.log('layout - client - data')
	// console.log(data)

	// setContext('backendAPIConfiguration', data?.body?.backendAPIConfiguration);
</script>

<main>
	{@render children?.()}
</main>
