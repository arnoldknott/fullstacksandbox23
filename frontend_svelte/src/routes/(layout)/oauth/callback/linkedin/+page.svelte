<script lang="ts">
	import { onMount } from 'svelte';

	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	onMount(() => {
		if (data.parentUrl && window.top) window.top.location.href = data.parentUrl;
	});
</script>

redirecting...
