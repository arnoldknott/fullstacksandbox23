<script lang="ts">
	import Display from '$components/Display.svelte';
	import NavigationCard from '$components/NavigationCard.svelte';

	const sidebars = [
		{
			name: 'Recursion in sidebar',
			description:
				'Creates recursive sidebar items which can either be links or folders containing more sidebar items.',
			url: 'sidebar/recursion'
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
