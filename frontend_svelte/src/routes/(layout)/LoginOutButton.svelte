<script lang="ts">
	import { IdentityProvider } from '$lib/identityProvider';

	let {
		loggedIn,
		parentUrl,
		provider = IdentityProvider.MICROSOFT
	}: { loggedIn: boolean; parentUrl?: string; provider?: IdentityProvider } = $props();
</script>

{#if !loggedIn}
	<button class="btn btn-neutral shadow-neutral ml-2 rounded-full shadow-sm" aria-label="Log In">
		{#if parentUrl}
			<a href={`/login/${provider}?parent-url=${encodeURIComponent(parentUrl)}`}>Log in</a>
		{:else}
			<a href={`/login/${provider}`}>Log in</a>
		{/if}
	</button>
{:else}
	<button
		class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
		aria-label="Log Out"
	>
		<a href={`/logout/${provider}`}>Log out</a>
	</button>
{/if}
