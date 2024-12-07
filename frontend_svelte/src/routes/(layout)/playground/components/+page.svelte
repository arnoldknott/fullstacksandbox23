<script lang="ts">
	import VerticalTabs from '$components/VerticalTabs.svelte';
	import Title from '$components/Title.svelte';
	import Tabs from '$components/Tabs.svelte';
	import type { Tab } from '$lib/types';

	const tabs: Tab[] = [
		{
			header: 'Left Tab',
			content: 'Some content in the left tab.',
		},
		{
			header: 'Right Tag',
			content: 'The tab, that is activated by default is the one on the right side.',
			active: true
		}
	]
</script>

<div class="mx-5">
	<!-- <h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">Vertical Tabs</h1> -->
	<Title>Vertical Tabs</Title>
	<VerticalTabs />
	<hr class="mx-5 my-12 h-2 bg-neutral-500 opacity-100 dark:opacity-50" />

	<Title>Tabs</Title>
	<Tabs {tabs}>Some Text common to all tabs</Tabs>
	<hr class="mx-5 my-12 h-2 bg-neutral-500 opacity-100 dark:opacity-50" />
</div>
