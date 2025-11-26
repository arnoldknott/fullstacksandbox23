<script lang="ts">
	import NavigationCard from '$components/NavigationCard.svelte';
	import Display from '$components/Display.svelte';
	import Loreum from '../Loreum.svelte';
	import Title from '$components/Title.svelte';

	const sidebars = [
		{
			name: 'Page 1',
			description: 'First page linked from sidebar.',
			url: 'hierarchy-scroll/page1'
		},
		{
			name: 'Page 2',
			description: 'Second page linked from sidebar.',
			url: 'hierarchy-scroll/page2'
		},
		{
			name: 'Page 3',
			description: 'Third page linked from sidebar.',
			url: 'hierarchy-scroll/page3'
		},
		{
			name: 'Page 4',
			description: 'Fourth page linked from sidebar.',
			url: 'hierarchy-scroll/page4'
		}
	];
</script>

<Display>Iteration elements with hierarchical pages</Display>

<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
	{#each sidebars as item (item.name)}
		<div>
			<Title id={item.name.replaceAll(' ', '-').toLowerCase()}>{item.name}</Title>
			<NavigationCard title={item.name} href={item.url}>
				{item.description}
			</NavigationCard>
			<Loreum repetition={1} />
		</div>
	{/each}
</div>
