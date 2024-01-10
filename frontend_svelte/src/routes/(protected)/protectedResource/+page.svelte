<script lang="ts">
  import type { PageData } from './$types';
  export let data: PageData;
  // console.log(data);
</script>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
    Protected Resource
  </h1>
</div>


{#await data}
  <p>...loading</p>
{:then data}
  <code><pre>{JSON.stringify(data.protectedResource, null, ' ')}</pre></code>
{:catch error}
  <p>{error.message}</p>
{/await}

