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
<Heading class="mx-5 md:mx-35" id="navigation-elements">Navigation Elements</Heading>
<div class="mb-5 grid grid-cols-1 gap-8 md:mx-30 md:grid-cols-2">
	{#each navigation as item (item.name)}
		<NavigationCard title={item.name} href={item.url}>
			{item.description}
		</NavigationCard>
	{/each}
</div>

<Heading class="mx-5 md:mx-35" id="components">Components</Heading>

<Heading class="mx-5 md:mx-35" id="services">Services</Heading>
