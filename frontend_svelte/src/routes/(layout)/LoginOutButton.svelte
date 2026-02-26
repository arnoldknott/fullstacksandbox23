<script lang="ts">
	let { loggedIn, parentUrl }: { loggedIn: boolean; parentUrl?: string } = $props();
</script>

{#if !loggedIn}
	<button class="btn btn-neutral shadow-neutral ml-2 rounded-full shadow-sm" aria-label="Log In">
		{#if parentUrl}
			<a href={`/login?parentURL=${encodeURIComponent(parentUrl)}`}>Log in</a>
		{:else}
			<a href="/login">Log in</a>
		{/if}
	</button>
{:else}
	<button
		class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
		aria-label="Log Out"
	>
		<a href="/logout">Log out</a>
	</button>
{/if}
