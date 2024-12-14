<script lang="ts">
	import VerticalTabs from '$components/VerticalTabs.svelte';
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import Tabs from '$components/Tabs.svelte';
	import Card from '$components/Card.svelte';
	import type { Tab } from '$lib/types';
	// import { createRawSnippet, type Snippet } from 'svelte';
	import UserForm from '$components/UserForm.svelte';
	import type { IOverlay } from 'flyonui/flyonui';

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

	const loadHSOverlay = async () => {
		const { HSOverlay } = await import('flyonui/flyonui.js');
		return HSOverlay;
	};

	let myModal: HTMLElement;
	let overlay: IOverlay | undefined = $state();

	$effect(() => {
		loadHSOverlay().then((loadHSOverlay) => {
			overlay = new loadHSOverlay(myModal);
		});
	});

	const openModal = () => {
		overlay?.open();
	};

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

	<Title>Stuff from Flyonui</Title>

	<Title>Drawer (Sidebar)</Title>
	<button
		type="button"
		class="btn btn-primary"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="overlay-example"
		data-overlay="#overlay-example">Open drawer</button
	>

	<div
		id="overlay-example"
		class="overlay drawer drawer-start hidden overlay-open:translate-x-0"
		role="dialog"
		tabindex="-1"
	>
		<div class="drawer-header">
			<h3 class="drawer-title">Drawer Title</h3>
			<button
				type="button"
				class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
				aria-label="Close"
				data-overlay="#overlay-example"
			>
				<span class="icon-[tabler--x] size-5"></span>
			</button>
		</div>
		<div class="drawer-body">
			<p>
				Some text as placeholder. In real life you can have the elements you have chosen. Like,
				text, images, lists, etc.
			</p>
		</div>
		<div class="drawer-footer">
			<button type="button" class="btn btn-secondary btn-soft" data-overlay="#overlay-example"
				>Close</button
			>
			<button type="button" class="btn btn-primary">Save changes</button>
		</div>
	</div>

	<HorizontalRule />

	<Title>Card</Title>
	<div class="card sm:max-w-sm">
		<div class="card-body">
			<h5 class="card-title mb-2.5">Body of a Card here</h5>
			<p class="mb-4">
				Soe text to fill in the body fo the card. This could be anything here. But for now just text
				filling in here.
			</p>
			<div class="card-actions">
				<button class="btn btn-primary">Card button</button>
			</div>
		</div>
	</div>
	<HorizontalRule />
</div>
