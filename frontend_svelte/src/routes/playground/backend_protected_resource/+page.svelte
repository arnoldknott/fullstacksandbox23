<script lang="ts">
  import type { PageData } from './$types';
	export let data: PageData;
</script>

{#if data}
<code><pre>{JSON.stringify(data.body, null, ' ')}</pre></code>
{/if}