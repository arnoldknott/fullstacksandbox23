<script lang="ts">
	import Guard from '$components/Guard.svelte';
	import Title from '$components/Title.svelte';
	import { page } from '$app/stores';
	// import NavButton from '$components/NavButton.svelte';
</script>

<Guard>
	<Title>Welcome inside {$page.data.session.microsoftProfile.displayName} - this is your Dashboard</Title>
</Guard>
