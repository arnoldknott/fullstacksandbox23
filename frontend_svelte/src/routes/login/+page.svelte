<script lang="ts">
	// import { onMount } from 'svelte';
	// // import { signIn } from '$lib/oauth.js';
	// // import Authentication from '$lib/oauth.js';
	// import { auth_instance_store } from '$lib/stores.js';
	// // import { get } from 'svelte/store';
	// // import Authentication  from '$lib/oauth.js';
	// // import type { PageData } from './$types';
	// // export let data: PageData;

	// let origin = 'undefined'
	// if (typeof window !== 'undefined') {
  //   origin = location.origin
	// 	// console.log('location', location)
	// 	// console.log('host', origin)
  // }

	// // let msal: PublicClientApplication | undefined
  // // msalInstanceStore.subscribe(value => {
  // //   msal = value
  // // })
	// const auth = $auth_instance_store
	// onMount(async () => {
	// 	if (auth !== undefined) {
	// 		console.log('login - client - auth')
	// 		console.log(auth)
	// 		await auth.signIn( origin )
	// 		auth_instance_store.set(auth);
	// 	}
	// });
</script>


<!-- <script lang="ts">
	import { goto } from '$app/navigation';
	// export const ssr = false;
	import UserForm from '$components/UserForm.svelte';
	import { onMount } from 'svelte';
	import { user_store } from '$lib/stores.js';

	export let form;
	// TBD: check if user is logged in (protected route) - this form status check is not enough!
	// TBD: onMount delays the redirect, so the user sees the previous information for a short time
	// TBD catch errors and display to user
	onMount(() => {
		if ($user_store?.loggedIn && form?.status === 200) {
			goto(form.redirect);
		}
	});
</script>

<UserForm /> -->
