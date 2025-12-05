<script lang="ts">
	import NavigationCard from '$components/NavigationCard.svelte';
	import Display from '$components/Display.svelte';

	const navbars = [
		{
			name: '🚧 Construction 🚧',
			description: 'Development process of top navbar.',
			url: 'navbar/development'
		},
		{
			name: 'Layout before sidebar',
			description: 'Replicates the layout and scrolling behavior before sidebar was added and breaks out of current layout including theming.',
			url: 'navbar/before-sidebar'
		}
	];
</script>

<Display>Navbars</Display>

<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
	{#each navbars as item (item.name)}
		<NavigationCard title={item.name} href={item.url}>
			{item.description}
		</NavigationCard>
	{/each}
</div>
