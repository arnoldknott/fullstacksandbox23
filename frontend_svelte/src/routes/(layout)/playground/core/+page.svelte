<script lang="ts">
	import Title from '$components/Title.svelte';

	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
	let urlClient = $state('undefined');
	if (typeof window !== 'undefined') {
		urlClient = location.href;
	}
</script>

<div class="mx-5">
	<Title id="getting-health-status-of-backendapi-connection-to-keyvault"
		>Getting health status of backendAPI connection to keyvault:</Title
	>
</div>

<code><pre>{JSON.stringify(data.keyvaultHealthBackend, null, ' ')}</pre></code>

<div class="mx-5">
	<Title id="location-name-client-side">Location name - client side:</Title>
</div>

<code>{urlClient}</code>

<div class="mx-5">
	<Title id="url-of-this-page-svelte-server-side">URL of this page - Svelte server side:</Title>
</div>

<code>{JSON.stringify(data.urlServer, null, ' ')}</code>
