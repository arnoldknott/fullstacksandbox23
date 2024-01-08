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
	// import { onMount } from 'svelte';
	import { user_store } from '$lib/stores';
	import NavButton from '$components/NavButton.svelte';
	import UserButton from '$components/UserButton.svelte';
	// import Authentication from '$lib/oauth.ts';
	// import { auth_instance_store } from '$lib/stores.ts';
	// import { createAuthentication } from '$lib/oauth.ts';
	import type { LayoutData } from './$types';
	// import Guard from '$components/Guard.svelte';

	// TBD: Get back to this later
	// import { microsoft_account_store } from '$lib/stores.ts';
	// import type { User } from 'src/types.d.ts';

	export let data: LayoutData;
	console.log('layout - client - data')
	console.log(data)

	// if ($auth_instance_store === undefined) {
	// 	createAuthentication();
	// }

	// const createAuthentication = async () => {
	// 	if ($auth_instance_store === undefined) {
	// 		// const authInstance = new Authentication(data.client_id, data.authority);
	// 		// await authInstance.initialize();
	// 		// console.log('layout - client - created a new authInstance')
	// 		auth_instance_store.set(authInstance);
	// 		return authInstance;
	// 		// console.log('layout - client - auth_instance_store')
	// 		// console.log($auth_instance_store)
	// 	}
	// }
	// createAuthentication();
	// const auth = $auth_instance_store;
	// onMount( async () => {
		// auth_instance_store.set(auth);
		// const auth = await createAuthentication();
		// const auth = $auth_instance_store;
		// if($auth_instance_store){
		// 	console.log('layout - client - onMount - auth_instance_store')
		// 	console.log($auth_instance_store)
		// }

		// if( auth && auth.msalInstance ) {
		// 	// console.log('layout - client - get microsoft account')
		// 	try {
		// 		// const user = await auth.msalInstance.getAccount();
		// 		// console.log('layout - client - onMount - auth.msalInstance')
		// 		// console.log(auth.msalInstance)
		// 		// TBD: switch to using auth.getAccount()
		// 		// const microsoft_user = await auth.msalInstance.getAllAccounts();
		// 		const microsoft_user = await auth.getAccount();
		// 		// console.log('layout - client - onMount - user')
		// 		// console.log(microsoft_user)
		// 		if (microsoft_user){
		// 			microsoft_account_store.set(microsoft_user);
		// 			const user: User = {
		// 				loggedIn: true,
		// 				email: microsoft_user.username,
		// 				name: microsoft_user.name
		// 			}
		// 			user_store.set(user);
		// 		}
		// 		// const redirectResponse = await auth.msalInstance.handleRedirectPromise()
		// 		// console.log('layout - client - onMount - handleRedirectPromise')
		// 		// console.log(redirectResponse)
		// 		// microsoft_account_store.set(user);
		// 		// console.log('layout - client - user')
		// 		// console.log(user)
		// 	} catch (error) {
		// 		console.log('layout - client - error')
		// 		// console.log(error);
		// 		throw error;
		// 	}
		// }
		// console.log('layout - client - onMount - end - auth')
		// console.log(auth)
	// })

	if ($user_store?.loggedIn) {
		user_store.set(data.user);
	}

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
			{ data.userProfile.displayName }
			<!-- <Guard redirect="/">
				<NavButton url="/dashboard" link="Dashboard" />
			</Guard> -->
		</div>
		<div class="flex space-x-4">
			<!-- <NavButton url="/user" link="User" /> -->
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
</main>
