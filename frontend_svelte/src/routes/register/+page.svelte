<script lang="ts">
	import { goto } from '$app/navigation';
	// export const ssr = false;
	import UserForm from '$components/UserForm.svelte';
	import { onMount } from 'svelte';
	import { user_store } from '$lib/stores.js';

	export let form;
	onMount(() => {
		if ($user_store?.loggedIn && form?.status === 200) {
			goto(form.redirect);
		}
	});
</script>

<UserForm type="signup" />
