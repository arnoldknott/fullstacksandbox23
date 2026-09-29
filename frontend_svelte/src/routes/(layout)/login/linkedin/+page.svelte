<script lang="ts">
	import { onMount } from 'svelte';

	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	onMount(() => {
		if (window.self !== window.top && window.top) {
			localStorage.setItem('session_id', data.sessionId);
			window.top.location.href = data.loginUrl;
		} else {
			window.location.href = data.loginUrl;
		}
	});
</script>

Logging in with LinkedIn...
