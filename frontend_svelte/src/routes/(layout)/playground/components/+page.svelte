<script lang="ts">
	import VerticalTabs from '$components/VerticalTabs.svelte';
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import Tabs from '$components/Tabs.svelte';
	import Card from '$components/Card.svelte';
	import type { Tab } from '$lib/types';
	// import { createRawSnippet, type Snippet } from 'svelte';
	import UserForm from '$components/UserForm.svelte';

	const tabs: Tab[] = [
		{
			header: 'Left Tab',
			content: 'Some content in the left tab.'
		},
		{
			header: 'Right Tag',
			content: 'The tab, that is activated by default is the one on the right side.',
			active: true
		}
	];

	// const createdComponent: Snippet = createRawSnippet(() => {
	// return {
	// 	render: () => ``
	// 	// setup: (element: Element) => {}
	// };
	// });

	// let isDrawerOpen = $state(false);

	// const toggleDrawer = () => {
	// 	isDrawerOpen = !isDrawerOpen;
	// 	console.log('Drawer toggled to ' + isDrawerOpen);
	// }
	// const closeDrawer = () => isDrawerOpen = false;

	// let myTemperature: HTMLElement
</script>

<div class="grid grid-cols-2 gap-4">
	<Card
		title="FlyonUI 1"
		description="Playground and showcase for flyonUI components and design"
		href={`/playground/components/flyonui`}
	></Card>
	<Card
		title="Material Design 3"
		description="Playground and showcase for Material Design 3 components and design"
		href={`/playground/components/materialdesign`}
	></Card>
</div>

<div class="mx-5">
	<!-- <h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">Vertical Tabs</h1> -->
	<Title>Vertical Tabs</Title>
	<VerticalTabs />
	<HorizontalRule />

	<Title>Tabs</Title>
	<Tabs {tabs}>Some Text common to all tabs</Tabs>
	<HorizontalRule />

	<Title>User Form</Title>
	<div class="flex justify-center">
		<UserForm type="signup" />
		<UserForm type="login" />
	</div>
	<HorizontalRule />

	<Title>Card</Title>
	<Card
		title="Title of Card"
		description="Some text inside the card to describe what's going on here. The button links to this page."
		href=""
	></Card>
	<HorizontalRule />



</div>
