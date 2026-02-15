<script lang="ts">
	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
	console.log('Login page data', data);
	// put potenitally in onMount to avoid SSR issues
	if (window.self !== window.top && window.top) {
		// redirects the top-level window to the login URL,
		// which should trigger the OAuth flow in the main app context
		window.top.location.href = data.loginUrl;
	} else {
		// redirects the current window to the login URL,
		// which should trigger the OAuth flow in the main app context
		window.location.href = data.loginUrl;
	}
</script>

Logging in - client redirect.
