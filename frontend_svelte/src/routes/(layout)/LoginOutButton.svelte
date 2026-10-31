<script lang="ts">
	import { IdentityProvider } from '$lib/identityProvider';

	let {
		loggedIn,
		linkAccount = false,
		parentUrl,
		targetUrl,
		provider = IdentityProvider.MICROSOFT
	}: {
		loggedIn: boolean;
		linkAccount?: boolean;
		parentUrl?: string;
		targetUrl?: string;
		provider?: IdentityProvider;
	} = $props();

	let loginQuery = $derived(
		new URLSearchParams({
			...(linkAccount ? { intent: 'link' } : {}),
			...(targetUrl ? { 'target-url': targetUrl } : {}),
			...(parentUrl ? { 'parent-url': parentUrl } : {})
		}).toString()
	);
</script>

{#if !loggedIn}
	<button class="btn btn-neutral shadow-base-shadow ml-2 rounded-full shadow" aria-label="Log In">
		<a
			class="text-inherit!"
			data-sveltekit-preload-data="off"
			href={`/login/${provider}${loginQuery ? `?${loginQuery}` : ''}`}>Log in</a
		>
	</button>
{:else}
	<button
		class="btn btn-neutral btn-outline shadow-base-shadow ml-2 rounded-full shadow"
		aria-label="Log Out"
	>
		<a class="text-inherit!" href={`/logout/${provider}`}>Log out</a>
	</button>
{/if}
