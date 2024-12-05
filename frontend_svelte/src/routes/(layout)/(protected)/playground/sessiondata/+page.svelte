<script lang="ts">
	import Title from '$components/Title.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { page } from '$app/stores';
	const logSessionData = () => {
		console.log('=== routes - playground - userstore - $page.data.sessionData ===');
		console.log($page.data.session);
	};
</script>

<button class="m-4 rounded bg-blue-400 p-2" onclick={logSessionData}
	>Current $page.data.sessionData -> console</button
>

<Title>$page data session data</Title>
<JsonData data={$page.data.session} />

<Title>Page</Title>
<JsonData data={$page} />
