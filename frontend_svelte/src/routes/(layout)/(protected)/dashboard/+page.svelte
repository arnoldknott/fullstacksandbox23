<script lang="ts">
	import Guard from '$components/Guard.svelte';
	import Heading from '$components/Heading.svelte';
	import { page } from '$app/stores';
	// import NavButton from '$components/NavButton.svelte';
</script>

<Guard>
	<Heading
		>Welcome inside {$page.data.session.microsoftProfile.displayName} - this is your Dashboard</Heading
	>
</Guard>
