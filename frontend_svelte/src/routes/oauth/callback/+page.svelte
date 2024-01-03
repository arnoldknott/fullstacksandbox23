<script lang="ts">
	import { goto } from '$app/navigation';
  // import { redirect } from '@sveltejs/kit';
  // console.log('redirecting');
  
  // throw redirect(307, '/');
	// import { user_store } from '$lib/stores.js';
	// import { onMount } from 'svelte';

	// export let redirect = '/login';
  // goto('/');
	// const forward = () => {
	// 	onMount(() => {
	// 		goto(redirect);
	// 	});
	// 	return '';
	// };

	import { onMount } from 'svelte';

	import { auth_instance_store } from '$lib/stores.js';
	import { get } from 'svelte/store';
	


	onMount(async () => {
		const auth = get(auth_instance_store);
		// await auth.msalInstance.handleRedirectPromise();
		auth_instance_store.set(auth);
		console.log('callback - client - auth')
		console.log(auth);
		goto('/');

		// const initialMsalInstance =  JSON.parse( sessionStorage.getItem("msal.initialMsalInstance") )
		// console.log('callback - client - initialMsalInstance')
		// console.log(initialMsalInstance);

		// const msalResponseLoginRedirect = JSON.parse( sessionStorage.getItem("msal.responseLoginRedirect") )
		// console.log('callback - client - msalResponseLoginRedirect')
		// console.log(msalResponseLoginRedirect);
	});





</script>

redirecting...
<!-- {#if $user_store?.loggedIn}
	<slot />
{:else}
	<span />{forward()}
{/if} -->
