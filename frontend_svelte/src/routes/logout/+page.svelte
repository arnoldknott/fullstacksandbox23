<script lang="ts">
	import { user_store } from '$lib/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	// import type { PageData } from './$types';
	// export const data: PageData = '';

	$user_store = undefined;
	onMount(() => goto('/'));
</script>
