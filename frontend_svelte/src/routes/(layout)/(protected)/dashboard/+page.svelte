<script lang="ts">
	import Guard from '$components/Guard.svelte';
	// import { user_store } from '$lib/stores.js';
	import { page } from '$app/stores';
	// import NavButton from '$components/NavButton.svelte';
</script>

<Guard>
	<h1 class="m-5 text-center text-3xl text-primary">
		Welcome inside {$page.data.body.sessionData.microsoftProfile.displayName} - this is your Dashboard
	</h1>
</Guard>
