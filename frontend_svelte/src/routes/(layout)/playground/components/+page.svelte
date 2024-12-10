<script lang="ts">
	import VerticalTabs from '$components/VerticalTabs.svelte';
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import Tabs from '$components/Tabs.svelte';
	import Card from '$components/Card.svelte';
	import type { Tab } from '$lib/types';
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
			<h5 class="card-title mb-2.5">Welcome to Our Service</h5>
			<p class="mb-4">Discover the features and benefits that our service offers. Enhance your experience with our user-friendly platform designed to meet all your needs.</p>
			<div class="card-actions">
				<button class="btn btn-primary">Learn More</button>
			</div>
		</div>
	</div>
	<HorizontalRule />
</div>