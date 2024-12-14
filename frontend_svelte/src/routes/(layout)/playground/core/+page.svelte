<script lang="ts">
	import Title from '$components/Title.svelte';
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
	<Title>Getting health status of backendAPI connection to keyvault:</Title>
</div>

<code><pre>{JSON.stringify(backendInformation.keyvaultHealthBackend, null, ' ')}</pre></code>

<div class="mx-5">
	<Title>Location name - client side:</Title>
</div>

<code>{urlClient}</code>

<div class="mx-5">
	<Title>URL of this page - Svelte server side:</Title>
</div>

<code>{JSON.stringify(backendInformation.urlServer, null, ' ')}</code>
