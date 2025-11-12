<script lang="ts">
	import NavigationCard from '$components/NavigationCard.svelte';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	const navigation = [
		{
			name: 'Top Navbar',
			description:
				'across the upper part of the screent for top level application navigation and user login and logout.',
			url: 'user-interface/navbar'
		},
		{
			name: 'Sidebar',
			description: 'on the side of the screen for navigation for secondary application navigation.',
			url: 'user-interface/sidebar'
		},
		{
			name: 'Panes',
			description: 'sectioning the screen for displaying content in a split view.',
			url: 'user-interface/panes'
		},
		{
			name: 'Tabs',
			description: 'switching to different aspects of a specific content.',
			url: 'user-interface/tabs'
		}
	];
</script>

<svelte:head>
	<title>FSSB23 - User Interface</title>
	<meta name="description" content="Provides examples of user interface components and layouts." />
</svelte:head>

<Display>User Interface Elements</Display>

<div class="mx-5 my-5 grid grid-cols-12 gap-5">
	<div
		class="col-span-12 md:col-start-2 md:col-end-11 xl:col-span-6 xl:col-start-1 xl:col-end-7 2xl:col-start-2 2xl:col-end-6"
	>
		<Heading id="navigation-elements">Navigation Elements</Heading>
		<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
			{#each navigation as item (item.name)}
				<NavigationCard title={item.name} href={item.url}>
					{item.description}
				</NavigationCard>
			{/each}
		</div>
	</div>

	<div
		class="col-span-12 md:col-start-2 md:col-end-11 xl:col-span-6 xl:col-start-7 xl:col-end-12 xl:mt-30 2xl:col-start-8 2xl:col-end-11"
	>
		<Heading id="components">Components</Heading>
		<div>Components coming here.</div>
	</div>

	<div
		class="col-span-12 md:col-start-2 md:col-end-11 xl:col-span-6 xl:col-start-1 xl:col-end-7 xl:mt-30 2xl:col-start-2 2xl:col-end-6"
	>
		<Heading id="services">Services</Heading>
		<div>Services coming here.</div>
	</div>
</div>
