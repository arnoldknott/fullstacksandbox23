<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { page } from '$app/stores';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	const logSessionData = () => {
		console.log('=== routes - playground - userstore - $page.data.sessionData ===');
		console.log($page.data.session);
	};
</script>

<button class="m-4 rounded bg-blue-400 p-2" onclick={logSessionData}
	>Current $page.data.sessionData -> console</button
>

<Heading>$page data session data</Heading>
<JsonData data={$page.data.session} />

<HorizontalRule />

<Heading>Page</Heading>
<JsonData data={$page} />

<HorizontalRule />
