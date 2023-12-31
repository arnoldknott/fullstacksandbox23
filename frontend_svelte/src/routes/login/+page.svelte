<script lang="ts">
	import { onMount } from 'svelte';
	import { signIn } from '$lib/oauth.js';
	import type { PageData } from './$types';
	export let data: PageData;

	let host = 'undefined'
	if (typeof window !== 'undefined') {
    host = location.href
  }

	onMount(() => {
		signIn( data.client_id, data.authority, host )
	});
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
