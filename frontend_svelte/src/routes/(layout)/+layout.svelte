<script lang="ts">
	import NavButton from '$components/NavButton.svelte';
	import UserButton from '$components/UserButton.svelte';
	// import type { LayoutData } from '../$types';
	import type { Snippet } from 'svelte';
	import { page } from '$app/stores';
	import Guard from '$components/Guard.svelte';

	// let { data, children }: { data: LayoutData; children: Snippet } = $props();
	let { children }: { children: Snippet } = $props();
	// const session = data?.sessionData;
	// const loggedIn = session?.loggedIn || false;
	const { loggedIn } = $page.data.session || false;
	// const { session } = $page.data;

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
			<NavButton url="/playground" link="Playground" />
			<Guard>
				<NavButton url="/protected" link="Protected" />
				<NavButton url="/dashboard" link="Dashboard" />
			</Guard>
		</div>
		<div class="flex space-x-4">
			<!-- Move this to component user button -->
			<!-- Implement check for user picture size and show svg instead, if no user picture available -->

			<!-- {#if loggedIn} -->
			<Guard>
				<img class="h-12 w-12 rounded-full" src="/api/v1/user/me/picture" alt="you" />
				{$page.data.session.microsoftProfile.displayName}
				<!-- TBD: remove the following one: -->
				<!-- {#if userPictureURL}
					<img class="h-12 w-12 rounded-full" src={userPictureURL} alt="you" />
				{/if} -->
			</Guard>
			<!-- {/if} -->
			<!-- Change this to using $page.data -> user -->
			{#if !loggedIn}
				<!-- <Guard> -->
				<!-- <NavButton url="/register" link="Register" invert /> -->
				<!-- data-sveltekit-preload-data="false" -->
				<!-- TBD: remove it here and set in hooks.Server.ts -->
				<NavButton pre_load={false} url={`/login?targetURL=${$page.url.href}`} link="Login" />
			{:else}
				<UserButton />
				<!-- needs to redirect to /home and delete session information -->
				<!-- TBD: write tests for logout -->
				<!-- data-sveltekit-preload-data="false" -->
				<NavButton pre_load={false} url="/logout" link="Logout" />
			{/if}
		</div>
	</div>
</nav>

<!-- <JsonData data={$page}></JsonData> -->

<div >
	{@render children?.()}
</div>

