<script lang="ts">
	import NavigationCard from '$components/NavigationCard.svelte';
	import Display from '$components/Display.svelte';

	const sidebars = [
		{
			name: 'Standalone',
			description: 'A stand-alone side bar.',
			url: 'sidebar/stand-alone'
		},
		{
			name: 'Adding Scrollspy',
			description: 'Adds scrollspy functionality within page to sidebar.',
			url: 'sidebar/scrollspy'
		},
		{
			name: 'Integrate with Navbar',
			description: 'integrates sidebar with default top navbar.',
			url: 'sidebar/navbar'
		},
		{
			name: 'Combined Navbar and Scrollspy',
			description: 'combines both default navbar integration and scrollspy.',
			url: 'sidebar/navbar-scrollspy'
		},
		{
			name: 'Adding collapse to icon sidebar',
			description: 'Adds collapse to a icon sidebar.',
			url: 'sidebar/collapse'
		},
		{
			name: 'Merge with existing navbar',
			description:
				'Merges sidebar with existing navbar and adds a main menu in sidebar for small screens - the previous dropdown in the navbar.',
			url: 'sidebar/merge'
		},
		{
			name: 'Segmenting code',
			description:
				'Segments the code from navbar and sidebar into snippets and components and parameterizes them for reusability and maintainability.',
			url: 'sidebar/segmenting'
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
