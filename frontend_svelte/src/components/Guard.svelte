<script lang="ts">
	import { goto } from '$app/navigation';
	import { user_store } from '$lib/stores.js';
	import { onMount } from 'svelte';

	let { redirect = 'login', children } = $props();

	const forward = () => {
		onMount(() => {
			goto(redirect);
		});
		return '';
	};
</script>

{#if $user_store?.loggedIn}
	{@render children?.()}
{:else}
	<span></span>{forward()}
{/if}
