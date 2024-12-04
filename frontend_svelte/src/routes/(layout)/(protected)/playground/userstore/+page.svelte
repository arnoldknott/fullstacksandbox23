<script lang="ts">
	import { user_store } from '$lib/stores';
	import Title from '$components/Title.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { page } from '$app/stores';
	const logUserStore = () => {
		console.log(' === route: /playground/userstore === ');
		console.log($user_store);
		console.log('=== routes - playground - userstore - $page.data.body.sessionData ===');
		console.log($page.data.body.sessionData);
	};
	$effect(() => {
		const sessionCookie = document.cookie;
		console.log('sessionCookie', sessionCookie);
	});
</script>

<button class="m-4 rounded bg-blue-400 p-2" onclick={logUserStore}
	>Current $user_store -> console</button
>
<Title>User store</Title>
<JsonData data={$user_store} />

<Title>$page data session data</Title>
<JsonData data={$page.data.body.sessionData} />

<Title>Page</Title>
<JsonData data={$page} />
