<script lang="ts">
	import { goto } from '$app/navigation';
	import { user_store } from '$lib/stores.js';
	import { onMount } from 'svelte';

	export let redirect = '/login';

	const forward = () => {
		onMount(() => {
			goto(redirect);
		});
		return '';
	};
</script>

{#if $user_store?.loggedIn}
	<slot />
{:else}
	<span />{forward()}
{/if}
