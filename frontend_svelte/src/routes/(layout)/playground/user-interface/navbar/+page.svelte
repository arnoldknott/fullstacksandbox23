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
			description:
				'Replicates the layout and scrolling behavior before sidebar was added and breaks out of current layout including theming.',
			url: 'navbar/before-sidebar'
		},
		{
			name: 'Adds sidebar',
			description:
				'Adds a dummy sidebar and reorganizes the layout to fit with scrolling behavior.',
			url: 'navbar/with-sidebar'
		},
		{
			name: 'Scroll off by javascript',
			description:
				'Changes the scrolling off on top from "sticky" in terraform to javascript "onScroll" event.',
			url: 'navbar/hide-by-javascript'
		},
		{
			name: 'Debug scrollspy with scroll off by Javascript',
			description:
				'Takes the sidebar and Sidebar united with scroll-off by Javascript and new document layout - debugs scrollspy errors, especially for foreign pages.',
			url: 'navbar/debug-scrollspy'
		},
		{
			name: 'Replacing scrollspy with custom implementation',
			description: 'Removes scrollspy and implements a scroll tracking by intersection observer.',
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
