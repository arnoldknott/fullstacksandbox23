<script lang="ts">
  // /** @type {import('./$types').PageData} */
	// import type { PageData } from './$types';
	// export let data: PageData;
  // import { onMount } from 'svelte';
  // import { getBackend } from '$lib/backend';

  // let authVerification
  // onMount(async () => {
  //   authVerification = await getBackend('/api/v1/core/health');
  //   console.log('authVerification', authVerification);
  // });
  import { getBackend } from '$lib/backend';
  import { onMount} from 'svelte';
  // import { getAccessToken } from '$lib/oauth.ts';

  let health
  onMount(async () => {
    // const accessToken = await getAccessToken();
    // console.log('protected_resource - client - accessToken');
    // console.log(accessToken);
    await getBackend('/api/v1/protected_resource')
    // await fetch (this.action,{
    //   method: 'GET',
    //   headers: {
    //     'Content-Type': 'application/json',
    //     'Authentication': `Bearer ${accessToken}`,
    //   },
    // })
    // })
    // health = await getBackend('/api/v1/protected_resource');
    // console.log('health', health);
  });
  

</script>

{#if health}
<code><pre>{JSON.stringify(health, null, ' ')}</pre></code>
{/if}