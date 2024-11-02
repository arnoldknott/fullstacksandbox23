<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	// export let data: PageData;
	let { data }: { data: PageData } = $props();
	const demo_resources = data.demoResources;
</script>

<!-- <code><pre>{JSON.stringify(demo_resources, null, ' ')}</pre></code> -->

{#each demo_resources as demo_resource}
	<Title>{demo_resource.name}</Title>
	<JsonData data={demo_resource} />
{/each}
