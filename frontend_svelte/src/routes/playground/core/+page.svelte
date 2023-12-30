<script lang="ts">
	import type { PageData } from './$types';
	export let data: PageData;
  export let url_client = 'undefined'
  if (typeof window !== 'undefined') {
    url_client = location.href
  }
  // console.log( host );
</script>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		Getting health status of environment:
	</h1>
</div>

<code><pre>{JSON.stringify(data.keyvaultHealth, null, ' ')}</pre></code>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		Location name - client side:
	</h1>
</div>

<code>{ url_client }</code>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		URL of this page - server side:
	</h1>
</div>

<code>{JSON.stringify(data.url, null, ' ')}</code>