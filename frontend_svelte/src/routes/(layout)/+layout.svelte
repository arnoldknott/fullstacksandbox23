<script lang="ts">
	// import { onMount } from 'svelte';
	import NavButton from '$components/NavButton.svelte';
	import UserButton from '$components/UserButton.svelte';
	// import { redisCache } from '$lib/redisCache';
	// import { user_store } from '$lib/stores';
	import type { LayoutData } from '../$types';
	import type { Snippet } from 'svelte';
	import { page } from '$app/stores';
	// import JsonData from '$components/JsonData.svelte';
	// import Guard from '$components/Guard.svelte';
	// import type { User } from 'src/types.d.ts';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();
	const session = data?.body?.sessionData;
	const loggedIn = session?.loggedIn || false;
	// console.log('layout - session');
	// console.log(session);
	// console.log('layout - loggedIn');
	// console.log(loggedIn);

	// let userPictureURL: URL | undefined = $state(undefined);
	// onMount(async () => {
	// 	// this call does not have any authentication - remove it!
	// 	const response = await fetch('/api/v1/user/me/picture', { method: 'GET' });
	// 	if (!response.ok && response.status !== 200) {
	// 		console.log('layout - userPictureURL - response not ok');
	// 		console.log(response);
	// 	} else {
	// 		const pictureBlob = await response.blob();
	// 		// console.log('layout - userPictureURL - pictureBlob');
	// 		// console.log(pictureBlob);
	// 		if (pictureBlob.size === 0) {
	// 			console.log('layout - userPictureURL - no User picture available');
	// 			console.log(pictureBlob);
	// 		} else {
	// 			userPictureURL = URL.createObjectURL(pictureBlob);
	// 			// console.log('layout - userPictureURL');
	// 			// console.log(userPictureURL);
	// 		}
	// 	}
	// });
</script>

<nav class="mx-2 p-2">
	<div class="flex w-full flex-wrap items-center justify-between">
		<div class="flex-grow space-x-4">
			<NavButton url="/" link="Home" />
			<NavButton url="/docs" link="Docs" />
			{#if loggedIn}
				<NavButton url="/playground" link="Playground" />
				<NavButton url="/protectedResource" link="Protected" />
				<NavButton url="/dashboard" link="Dashboard" />
			{/if}
			<!-- <Guard redirect="/">
				<NavButton url="/dashboard" link="Dashboard" />
			</Guard> -->
		</div>
		<div class="flex space-x-4">
			<!-- <NavButton url="/user" link="User" /> -->
			<!-- Move this to component user button -->
			<!-- Implemnt check for user picture size and show svg instead, if no user picture available -->

			{#if loggedIn}
				<img class="h-12 w-12 rounded-full" src="/api/v1/user/me/picture" alt="you" />
				<!-- TBD: add the userProfile to the session - don't use the microsoft acount here! -->
				<!-- {session.userProfile.displayName} -->
				{session.microsoftAccount.name}
				<!-- TBD: remove the following one: -->
				<!-- {#if userPictureURL}
					<img class="h-12 w-12 rounded-full" src={userPictureURL} alt="you" />
				{/if} -->
			{/if}
			<!-- Change this to using $page.data -> user -->
			{#if !loggedIn}
				<!-- <NavButton url="/register" link="Register" invert /> -->
				<!-- data-sveltekit-preload-data="false" -->
				<!-- TBD: remove it here and set in hooks.Server.ts -->
				<NavButton pre_load="false" url={`/login?targetURL=${$page.url.href}`} link="Login" />
			{:else}
				<UserButton />
				<!-- needs to redirect to /home and delete session information -->
				<!-- TBD: write tests for logout -->
				<!-- data-sveltekit-preload-data="false" -->
				<NavButton pre_load="false" url="/logout" link="Logout" />
			{/if}
		</div>
	</div>
</nav>

<!-- <JsonData data={$page}></JsonData> -->

<main>
	{@render children?.()}
</main>
