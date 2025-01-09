<script lang="ts">
    import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';

    let {data}: {data: PageData} = $props();
</script>

<Heading>My user Profile in this app</Heading>
<JsonData data={data.session?.userProfile} />