<script lang="ts">
	import NavigationCard from '$components/NavigationCard.svelte';
	import Display from '$components/Display.svelte';

	const sidebars = [
		{
			name: 'Standalone',
			description: '',
			url: 'sidebar/stand-alone'
		},
		{
			name: 'Adding Scrollspy',
			description: '',
			url: 'sidebar/scrollspy'
		},
		{
			name: 'Integrate with Navbar',
			description: '',
			url: 'sidebar/navbar'
		}
	];
</script>

<Display>Sidebars</Display>

<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
	{#each sidebars as item (item.name)}
		<NavigationCard title={item.name} href={item.url}>
			{item.description}
		</NavigationCard>
	{/each}
</div>
