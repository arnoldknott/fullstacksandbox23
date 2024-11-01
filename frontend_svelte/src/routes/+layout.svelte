<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { user_store } from '$lib/stores';
	import NavButton from '$components/NavButton.svelte';
	import UserButton from '$components/UserButton.svelte';
	import type { LayoutData } from './$types';
	// import JsonData from '$components/JsonData.svelte';
	// import Guard from '$components/Guard.svelte';
	// import type { User } from 'src/types.d.ts';

	export let data: LayoutData;
	// console.log('layout - client - data')
	// console.log(data)

	// gather these three in one session object
	// $: userProfile = data?.body?.userProfile;
	// $: userAgent = data?.body?.userAgent;
	// $: loggedIn = data?.body?.loggedIn || false;
	const session = data?.body?.sessionData;
	const loggedIn = session?.loggedIn || false;

	if (loggedIn) {
		user_store.set(session);
	}

	// console.log('layout - client - userProfile')
	// console.log(userProfile)

	// console.log('layout - client - data')
	// console.log(data)
	// console.log('layout - client - $page.data')
	// console.log($page.data)

	// TBD use $page.data for that - that's the standard store, and user logged in information is relevant everywhere.
	// if ($user_store?.loggedIn) {
	// 	user_store.set(data.user);
	// }

	let userPictureURL: URL = undefined;
	onMount(async () => {
		const response = await fetch('/api/v1/user/me/picture', { method: 'GET' });
		if (!response.ok && response.status !== 200) {
			console.log('layout - userPictureURL - response not ok');
			console.log(response);
		} else {
			const pictureBlob = await response.blob();
			if (pictureBlob.size === 0) {
				console.log('layout - userPictureURL - no User picture available');
				console.log(pictureBlob);
			} else {
				userPictureURL = URL.createObjectURL(pictureBlob);
			}
		}
	});

	// if (data?.loggedIn) {
	// 	$user_store = data;
	// }
</script>

<nav class="mx-2 p-2">
	<div class="flex w-full flex-wrap items-center justify-between">
		<div class="flex-grow space-x-4">
			<NavButton url="/" link="Home" />
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
				{session.userProfile.displayName}
				{#if userPictureURL}
					<img class="h-12 w-12 rounded-full" src={userPictureURL} alt="you" />
				{/if}
			{/if}
			<!-- Change this to using $page.data -> user -->
			{#if !loggedIn}
				<!-- <NavButton url="/register" link="Register" invert /> -->
				<!-- data-sveltekit-preload-data="false" -->
				<NavButton pre_load="false" url="/login" link="Login" />
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

<main>
	<slot />
	<!-- <JsonData data={ data?.body?.loggedIn }/> -->
	<!-- <JsonData data={ data.body }/> -->
</main>
