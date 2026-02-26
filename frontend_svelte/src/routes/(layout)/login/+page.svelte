<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();

	// put potenitally in onMount to avoid SSR issues
	onMount(() => {
		if (window.self !== window.top && window.top) {
			localStorage.setItem('session_id', data.sessionId);
			// redirects the top-level window to the login URL,
			// which should trigger the OAuth flow in the main app context
			// localStorage.setItem('session_id', data.sessionId);
			window.top.location.href = data.loginUrl;
		} else {
			// redirects the current window to the login URL,
			// which should trigger the OAuth flow in the main app context
			window.location.href = data.loginUrl;
		}
	});
</script>

Logging in - client redirect.
