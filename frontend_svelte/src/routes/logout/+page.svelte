<script lang="ts">
import { onMount } from 'svelte';
// import { signOut } from '$lib/oauth.js';
import { auth_instance_store } from '$lib/stores.js';
// import type { PageData } from './$types';
// export let data: PageData;
import { microsoft_account_store } from '$lib/stores.js';
import { user_store } from '$lib/stores.js';

let origin = 'undefined'
if (typeof window !== 'undefined') {
	origin = location.origin
	// console.log('location', location)
	// console.log('host', origin)
}

// const auth = $auth_instance_store
// console.log('login - client - auth')
// console.log(auth)
onMount( async () => {
	const auth = $auth_instance_store
	await auth.signOut( origin )
	auth_instance_store.set(auth);
	microsoft_account_store.set(undefined);
	user_store.set(undefined);
});

// onMount(() => {
// 	console.log('signing out')
// 	console.log(data)
// 	console.log(origin)
// 	signOut( data.client_id, data.authority, origin )
// });
</script>

logging out...

<!-- <script lang="ts">
	import { user_store } from '$lib/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	// import type { PageData } from './$types';
	// export const data: PageData = '';
	import { signOut } from '$lib/oauth.js';

	$user_store = undefined;
	onMount(() => {
		signOut();
		// goto('/');
	});
</script> -->
