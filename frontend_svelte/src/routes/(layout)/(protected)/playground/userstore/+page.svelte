<script lang="ts">
	import { user_store } from '$lib/stores';
	import Title from '$components/Title.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { page } from '$app/stores';
	// import { browser } from '$app/environment';
	const logUserStore = () => {
		console.log(' === route: /playground/userstore === ');
		console.log($user_store);
		console.log('=== routes - playground - userstore - $page.data.body.sessionData ===');
		console.log($page.data.body.sessionData);
	};
	// $effect to replace onMount:
	// onMount(() => {
	// 	const sessionCookie = document.cookie// browser.cookie.get('session_id');
	// 	console.log('sessionCookie', sessionCookie);
	// });
	$effect(() => {
		const sessionCookie = document.cookie; // browser.cookie.get('session_id');
		console.log('sessionCookie', sessionCookie);
	});
</script>

<button class="m-4 rounded bg-blue-400 p-2" onclick={logUserStore}
	>Current $user_store -> console</button
>
<!-- <code><pre>{JSON.stringify($user_store, null, ' ')}</pre></code> -->
<Title>User store</Title>
<JsonData data={$user_store} />

<Title>$page data session data</Title>
<JsonData data={$page.data.body.sessionData} />

<Title>Page</Title>
<JsonData data={$page} />
