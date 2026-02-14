<script lang="ts">
	// import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import type { Snippet } from 'svelte';
	// import { onMount } from 'svelte';

	// let { redirect = 'login', children } = $props();
	let { children }: { children: Snippet } = $props();
	// const { loggedIn } = page.data.session || false;
	let loggedIn = $derived(page.data.session?.loggedIn || false);
	// const forward = () => {
	// 	onMount(() => {
	// 		goto(redirect);
	// 	});
	// 	return '';
	// };
</script>

{#if loggedIn}
	{@render children?.()}
{:else}
	<span></span>
	<!-- {forward()} -->
{/if}
