<script lang="ts">
  import type { PageData } from './$types';
	export let data: PageData;
  const protected_resources = data.body;
</script>

{#if data}
<code><pre>{JSON.stringify(protected_resources, null, ' ')}</pre></code>
{/if}