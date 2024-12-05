<script lang="ts">
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
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		Getting health status of backendAPI connection to keyvault:
	</h1>
</div>

<code><pre>{JSON.stringify(backendInformation.keyvaultHealthBackend, null, ' ')}</pre></code>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		Location name - client side:
	</h1>
</div>

<code>{urlClient}</code>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		URL of this page - Svelte server side:
	</h1>
</div>

<code>{JSON.stringify(backendInformation.urlServer, null, ' ')}</code>
