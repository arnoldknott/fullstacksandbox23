<script lang="ts">
  // /** @type {import('./$types').PageData} */
	import type { PageData } from './$types';
	export let data: PageData;
</script>

<code><pre>{JSON.stringify(data.body, null, ' ')}</pre></code>