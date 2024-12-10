<script lang="ts">
	import VerticalTabs from '$components/VerticalTabs.svelte';
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import Tabs from '$components/Tabs.svelte';
	import Card from '$components/Card.svelte';
	import type { Tab } from '$lib/types';
	import { createRawSnippet, type Snippet } from 'svelte';
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

	let isDrawerOpen = $state(false);

	const toggleDrawer = () => {
		isDrawerOpen = !isDrawerOpen;
		console.log('Drawer toggled to ' + isDrawerOpen);
	}
	const closeDrawer = () => isDrawerOpen = false;	
</script>

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
	<Card title="Title of Card" description="Some text inside the card to describe what's going on here. The button links to this page." href=""></Card>
	<HorizontalRule	/>

	<Title>Stuff from Flyonui</Title>


	<Title>Drawer (Sidebar)</Title>
	<button type="button" class="btn btn-primary" aria-haspopup="dialog" aria-expanded="false" aria-controls="overlay-example" data-overlay="#overlay-example">Open drawer</button>

	
	<div id="overlay-example" class="overlay overlay-open:translate-x-0 drawer drawer-start hidden" role="dialog" tabindex="-1">
		<div class="drawer-header">
			<h3 class="drawer-title">Drawer Title</h3>
			<button type="button" class="btn btn-text btn-circle btn-sm absolute end-3 top-3" aria-label="Close" data-overlay="#overlay-example">
			<span class="icon-[tabler--x] size-5"></span>
			</button>
		</div>
		<div class="drawer-body">
			<p>
			Some text as placeholder. In real life you can have the elements you have chosen. Like, text, images, lists, etc.
			</p>
		</div>
		<div class="drawer-footer">
			<button type="button" class="btn btn-soft btn-secondary" data-overlay="#overlay-example">Close</button>
			<button type="button" class="btn btn-primary">Save changes</button>
		</div>
	</div>

	<HorizontalRule />

	<Title>Card</Title>
	<div class="card sm:max-w-sm">
		<div class="card-body">
			<h5 class="card-title mb-2.5">Body of a Card here</h5>
			<p class="mb-4">Soe text to fill in the body fo the card. This could be anything here. But for now just text filling in here.</p>
			<div class="card-actions">
				<button class="btn btn-primary">Card button</button>
			</div>
		</div>
	</div>
	<HorizontalRule />

	<Title>Modal</Title>
	<button type="button" class="btn btn-primary" aria-haspopup="dialog" aria-expanded="false" aria-controls="basic-modal" data-overlay="#basic-modal" > Open modal </button>

	<div id="basic-modal" class="overlay modal overlay-open:opacity-100 hidden" role="dialog" tabindex="-1">
	<div class="modal-dialog overlay-open:opacity-100">
		<div class="modal-content">
		<div class="modal-header">
			<h3 class="modal-title">Dialog Title</h3>
			<button type="button" class="btn btn-text btn-circle btn-sm absolute end-3 top-3" aria-label="Close" data-overlay="#basic-modal" >
			<span class="icon-[tabler--x] size-4"></span>
			</button>
		</div>
		<div class="modal-body">
			This is some placeholder content to show the scrolling behavior for modals. Instead of repeating the text in the
			modal, we use an inline style to set a minimum height, thereby extending the length of the overall modal and
			demonstrating the overflow scrolling. When content becomes longer than the height of the viewport, scrolling
			will move the modal as needed.
		</div>
		<div class="modal-footer">
			<button type="button" class="btn btn-soft btn-secondary" data-overlay="#basic-modal">Close</button>
			<button type="button" class="btn btn-primary">Save changes</button>
		</div>
		</div>
	</div>
	</div>
	<HorizontalRule />

</div>