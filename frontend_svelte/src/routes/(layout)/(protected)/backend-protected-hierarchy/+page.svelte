<script lang="ts">
	import type { PageData } from './$types';
	let data: PageData = $props();
	// console.log(data);
</script>

<div class="mx-5">
	<h1 class="text-primary mx-5 mt-0 mb-2 text-5xl leading-tight font-medium">Protected Resource</h1>
</div>

{#await data}
	<p>...loading</p>
{:then data}
	<code><pre>{JSON.stringify(data.protectedResource, null, ' ')}</pre></code>
{:catch error}
	<p>{error.message}</p>
{/await}
