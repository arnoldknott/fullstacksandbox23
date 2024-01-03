<!-- <script context="module" lang="ts">
		import Authentication from '$lib/oauth.js';
		import { auth_instance_store } from '$lib/stores.js';

	// import type { RequestHandler } from '@sveltejs/kit';
	// import type { LayoutData } from './$types';
	// import { auth_instance_store } from '$lib/stores.js';
	// import { user_store } from '$lib/stores.js';
	// import Authentication from '$lib/oauth.js';

	// export const get: RequestHandler<LayoutData> = async () => {
	// 	const authInstance = auth_instance_store.get();
	// 	const user = user_store.get();
	// 	console.log('layout - server - authInstance', authInstance)
	// 	console.log('layout - server - user', user)
	// 	return {
	// 		body: {
	// 			client_id: authInstance.client_id,
	// 			authority: authInstance.authority,
	// 			loggedIn: user.loggedIn,
	// 			user: user.user
	// 		}
	// 	};
	// };
</script> -->



<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { user_store } from '$lib/stores';
	import NavButton from '$components/NavButton.svelte';
	import UserButton from '$components/UserButton.svelte';
	import Authentication from '$lib/oauth.ts';
	import { auth_instance_store } from '$lib/stores.ts';
	// import { createAuthentication } from '$lib/oauth.ts';
	import type { LayoutData } from './$types';
	// import Guard from '$components/Guard.svelte';


	export let data: LayoutData;


	// if ($auth_instance_store === undefined) {
	// 	createAuthentication();
	// }

	const createAuthentication = async () => {
		if ($auth_instance_store === undefined) {
			const authInstance = new Authentication(data.client_id, data.authority);
			await authInstance.initialize();
			console.log('layout - client - created a new authInstance')
			auth_instance_store.set(authInstance);
		}
	}
	createAuthentication();
	const auth = $auth_instance_store;
	onMount( async () => {
		auth_instance_store.set(auth);
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
			<!-- <Guard redirect="/">
				<NavButton url="/dashboard" link="Dashboard" />
			</Guard> -->
		</div>
		<div class="flex space-x-4">
			<NavButton url="/login" link="Login" />
			<NavButton url="/logout" link="Logout" />
			<!-- <NavButton url="/user" link="User" /> -->
			{#if !$user_store?.loggedIn}
				<!-- <NavButton url="/register" link="Register" invert /> -->
				<NavButton url="/login" link="Login" />
			{:else}
				<UserButton />
				<!-- needs to redirect to /home and delete session information -->
				<!-- TBD: write tests for logout -->
				<NavButton url="/logout" link="Logout" />
			{/if}
		</div>
	</div>
</nav>

<main>
	<slot />
</main>
