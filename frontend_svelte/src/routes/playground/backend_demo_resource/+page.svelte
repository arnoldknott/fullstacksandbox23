<script lang="ts">
  // /** @type {import('./$types').PageData} */
	import type { PageData } from './$types';
	export let data: PageData;
  const demo_resources = data.body;
  // import { onMount } from 'svelte';
  // import { getBackend } from '$lib/backend';

  // let authVerification
  // onMount(async () => {
  //   authVerification = await getBackend('/api/v1/core/health');
  //   console.log('authVerification', authVerification);
  // });


</script>

<code><pre>{JSON.stringify(demo_resources, null, ' ')}</pre></code>