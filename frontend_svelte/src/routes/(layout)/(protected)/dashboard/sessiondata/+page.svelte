<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { page } from '$app/state';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
	const logSessionData = (data: Object | undefined) => {
		console.log('=== routes - playground - userstore - data.sessionData ===');
		console.log(data);
	};
</script>

<button class="m-4 rounded-sm bg-blue-400 p-2" onclick={() => logSessionData(data.session)}
	>Current data.sessionData -> console</button
>

<Heading>page data session data</Heading>
<!-- <JsonData data={page.data.session} /> -->
<JsonData data={data.session} />

<HorizontalRule />

<button class="m-4 rounded-sm bg-blue-400 p-2" onclick={() => logSessionData(page)}
	>Current page store -> console</button
>

<Heading>Page</Heading>
<JsonData data={page} />

<HorizontalRule />
