<script lang="ts">
  import type { PageData } from './$types';
  export let data: PageData;
  export const fromBackend = new Promise((resolve, reject) => {});
</script>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
    Protected Resource
  </h1>
</div>

{#await fromBackend}
  <p>...loading</p>
{:then data}
  <p>{data}</p>
{:catch error}
  <p>{error.message}</p>
{/await}
