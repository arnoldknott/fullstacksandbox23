<script lang="ts">
	import NavigationCard from '$components/NavigationCard.svelte';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	const navigation = [
		{
			name: 'Top Navbar',
			description:
				'The top navigation bar across the application for top level application navigation and user login and logout.',
			url: '/playground/user-interface/navbar'
		},
		{
			name: 'Sidebar',
			description: 'The sidebar navigation for secondary application navigation.',
			url: '/playground/user-interface/sidebar'
		}
	];
</script>

<svelte:head>
	<title>FSSB23 - User Interface</title>
	<meta name="description" content="Provides examples of user interface components and layouts." />
</svelte:head>

<Display>User Interface Elements</Display>

<div class="mx-5 my-5 grid grid-cols-12 gap-5">
	<Heading
		id="navigation-elements"
		class="col-span-12 lg:col-start-2 lg:col-end-11 xl:col-span-6 xl:col-start-1 xl:col-end-6 "
	>
		Navigation Elements
	</Heading>
	<div
		class="col-span-12 grid grid-cols-1 gap-8 md:grid-cols-2 lg:col-start-2 lg:col-end-11 xl:col-span-6 xl:col-start-1 xl:col-end-6"
	>
		{#each navigation as item (item.name)}
			<NavigationCard title={item.name} href={item.url}>
				{item.description}
			</NavigationCard>
		{/each}
	</div>

	<Heading
		id="components"
		class="col-span-12 lg:col-start-2 lg:col-end-11 xl:col-span-6 xl:col-start-7 xl:col-end-12"
	>
		Components
	</Heading>

	<Heading
		id="services"
		class="col-span-12 lg:col-start-2 lg:col-end-11 xl:col-span-6 xl:col-start-7 xl:col-end-12"
	>
		Services
	</Heading>
</div>
