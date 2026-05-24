<script lang="ts">
	import Heading from '$components/Heading.svelte';

	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
	let urlClient = $state('undefined');
	if (typeof window !== 'undefined') {
		urlClient = location.href;
	}
</script>

<div class="mx-5">
	<Heading>Getting health status of backendAPI connection to keyvault:</Heading>
</div>

<code><pre>{JSON.stringify(data.keyvaultHealthBackend, null, ' ')}</pre></code>

<div class="mx-5">
	<Heading>Location name - client side:</Heading>
</div>

<code>{urlClient}</code>

<div class="mx-5">
	<Heading>URL of this page - Svelte server side:</Heading>
</div>

<code>{JSON.stringify(data.urlServer, null, ' ')}</code>
