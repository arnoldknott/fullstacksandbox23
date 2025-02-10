<script lang="ts">
	import Guard from '$components/Guard.svelte';
	import Heading from '$components/Heading.svelte';
	import { page } from '$app/state';
</script>

<Guard>
	<Heading
		>Welcome inside {page.data.session.microsoftProfile.displayName} - this is your Dashboard</Heading
	>
</Guard>
