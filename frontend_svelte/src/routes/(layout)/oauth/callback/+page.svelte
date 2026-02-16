<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();

	// console.log('=== oauth - callback - client - data ===');
	// console.log(data);

	onMount(() => {
		localStorage.setItem('session_id', data.sessionId);
		if (window.top) {
			window.top.location.href = data.parentUrl;
		}
	});
</script>

redirecting...
