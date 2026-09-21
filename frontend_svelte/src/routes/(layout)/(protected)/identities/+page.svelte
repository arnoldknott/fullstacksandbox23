<script lang="ts">
	import NavigationCard from '$components/NavigationCard.svelte';

	let identities = [
		{
			name: 'All Identities',
			url: '/identities/all',
			description: 'Manage all your identities.'
		},
		{
			name: 'Microsoft Graph',
			url: '/identities/msgraph',
			description: 'Read your linked Microsoft Graph data.'
		}
	];
</script>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
	{#each identities as identity (identity.name)}
		<NavigationCard title={identity.name} href={identity.url}>{identity.description}</NavigationCard
		>
	{/each}
</div>
