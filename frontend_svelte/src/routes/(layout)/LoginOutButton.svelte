<script lang="ts">
	import { IdentityProvider } from '$lib/identityProvider';

	let {
		loggedIn,
		linkAccount = false,
		parentUrl,
		provider = IdentityProvider.MICROSOFT
	}: {
		loggedIn: boolean;
		linkAccount?: boolean;
		parentUrl?: string;
		provider?: IdentityProvider;
	} = $props();

	let loginQuery = $derived(
		new URLSearchParams({
			...(linkAccount ? { intent: 'link' } : {}),
			...(parentUrl ? { 'parent-url': parentUrl } : {})
		}).toString()
	);
</script>

{#if !loggedIn}
	<button class="btn btn-neutral shadow-neutral ml-2 rounded-full shadow-sm" aria-label="Log In">
		<a href={`/login/${provider}${loginQuery ? `?${loginQuery}` : ''}`}>Log in</a>
	</button>
{:else}
	<button
		class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
		aria-label="Log Out"
	>
		<a href={`/logout/${provider}`}>Log out</a>
	</button>
{/if}
