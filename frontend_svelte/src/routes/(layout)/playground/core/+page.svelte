<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import type { PageData } from './$types';
	let { data, urlClient }: { data: PageData; urlClient: string } = $props();
	// export let data: PageData;
	const backendInformation = data.body;
	// const backendInformation = $page.data.backendAPIConfiguration;
	// export let urlClient = 'undefined';
	if (typeof window !== 'undefined') {
		urlClient = location.href;
	}
</script>

<div class="mx-5">
	<Heading>Getting health status of backendAPI connection to keyvault:</Heading>
</div>

<code><pre>{JSON.stringify(backendInformation.keyvaultHealthBackend, null, ' ')}</pre></code>

<div class="mx-5">
	<Heading>Location name - client side:</Heading>
</div>

<code>{urlClient}</code>

<div class="mx-5">
	<Heading>URL of this page - Svelte server side:</Heading>
</div>

<code>{JSON.stringify(backendInformation.urlServer, null, ' ')}</code>
