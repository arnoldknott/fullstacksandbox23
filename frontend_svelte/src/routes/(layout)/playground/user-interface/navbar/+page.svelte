<script lang="ts">
	import Display from '$components/Display.svelte';
	import NavigationCard from '$components/NavigationCard.svelte';

	const navbars = [
		{
			name: 'Custom scrolling',
			description: 'Implements a scroll tracking by intersection observer.',
			url: 'navbar/custom-scrolltracking'
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
