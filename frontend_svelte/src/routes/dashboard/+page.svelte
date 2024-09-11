<script lang="ts">
	import Guard from '$components/Guard.svelte';
	import { user_store } from '$lib/stores.js';
	// import NavButton from '$components/NavButton.svelte';
</script>

<Guard>
	<h1 class="m-5 text-center text-3xl text-primary">
		Welcome inside {$user_store?.name} - this is your Dashboard
	</h1>
</Guard>
