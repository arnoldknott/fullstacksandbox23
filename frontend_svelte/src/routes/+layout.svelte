<script context="module" lang="ts">
	// Put the call to get_user_picture here, and pass the result to the component
	// make sure the user is logged in before using the load function here
</script>


<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { user_store } from '$lib/stores';
	import NavButton from '$components/NavButton.svelte';
	import UserButton from '$components/UserButton.svelte';
	import type { LayoutData } from './$types';
	// import Guard from '$components/Guard.svelte';
	// import type { User } from 'src/types.d.ts';

	export let data: LayoutData;
	// console.log('layout - client - data')
	// console.log(data)

	// TBD use $page.data for that - that's the standard store, and user logged in information is relevant everywhere.
	if ($user_store?.loggedIn) {
		user_store.set(data.user);
	}

	let userPictureURL: URL = undefined;
	onMount( async () => {
		const response = await fetch('/api/v1/user/me/picture', {method: 'GET'});
		console.log("layout - userPicture - response");
		console.log( response );
		console.log("layout - userPicture - response.ok");
		console.log( response.ok );
		console.log("layout - userPicture - response.status");
		console.log( response.status );
		console.log("layout - userPicture - response.headers");
		console.log( response.headers.get );
		const pictureBlob = await response.blob()
		userPictureURL = URL.createObjectURL(pictureBlob);// TBD - do this on the client!!
		console.log("layout - userPictureURL");
		console.log( userPictureURL );

		// const userPicture = await fetch('/api/v1/user/me/picture');
		// console.log("layout - userPictureRaw");
		// console.log( userPictureRaw );
		// const userPictureFile = await userPictureRaw.blob();
		// console.log("layout - userPictureFile");
		// console.log( userPictureFile );
		// userPictureURL = URL.createObjectURL(userPictureFile);// TBD - do this on the client!!
		// console.log("layout - userPictureURL");
		// console.log( userPictureURL );
	})


	// if (data?.loggedIn) {
	// 	$user_store = data;
	// }
</script>

<nav class="mx-2 p-2">
	<div class="flex w-full flex-wrap items-center justify-between">
		<div class="flex-grow space-x-4">
			<NavButton url="/" link="Home" />
			<NavButton url="/playground" link="Playground" />
			<NavButton url="/protectedResource" link="Protected" />
			{#if data?.userProfile}
				{ data.userProfile.displayName }
			{/if}
			<!-- <Guard redirect="/">
				<NavButton url="/dashboard" link="Dashboard" />
			</Guard> -->
		</div>
		<div class="flex space-x-4">
			<!-- <NavButton url="/user" link="User" /> -->
			<!-- Move this to component user button -->
			{#if userPictureURL}
				<img class="h-10 w-10 rounded-full" src={userPictureURL} alt="you" />
			{/if}
			<!-- Change this to using $page.data -> user -->
			{#if !$user_store?.loggedIn}
				<!-- <NavButton url="/register" link="Register" invert /> -->
				<!-- data-sveltekit-preload-data="false" -->
				<NavButton pre_load=false url="/login" link="Login" />
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
	{#if userPictureURL}
		<img class="h-100 w-100" src={userPictureURL} alt="you" />
	{/if}
</main>
