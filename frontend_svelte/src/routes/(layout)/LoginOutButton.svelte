<script lang="ts">
	let { loggedIn }: { loggedIn: boolean } = $props();
</script>

{#if !loggedIn}
	<button class="btn btn-neutral shadow-neutral ml-2 rounded-full shadow-sm" aria-label="Log In">
		<a href="/login">Log in</a>
	</button>
{:else}
	<button
		class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
		aria-label="Log Out"
	>
		<a href="/logout">Log out</a>
	</button>
{/if}
