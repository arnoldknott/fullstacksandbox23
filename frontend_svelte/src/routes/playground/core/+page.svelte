<script lang="ts">
	import type { PageData } from './$types';
	export let data: PageData;
  export const host = location.hostname
  console.log( host );
</script>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		Getting health status from keyvault
	</h1>
</div>

<code><pre>{JSON.stringify(data, null, ' ')}</pre></code>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		Host name
	</h1>
</div>

<code>{ host }</code>
