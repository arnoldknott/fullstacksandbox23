<!-- Rename the folder of this file "protected" into the real content -->

<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import NavigationCard from '$components/NavigationCard.svelte';

	const links = [
		{
			// TBD: don't do "_" in URLs, ideally just "/", but "-" is also ok.
			name: 'Via REST API',
			description:
				'The demo resources of the backend API service, retrieved through the backend REST API from the postgres database',
			url: '/restapi'
		},
		{
			name: 'Via Socket.IO',
			description:
				'The demo resources of the backend API service, retrieved through the backend REST API from the postgres database',
			url: '/socketio'
		}
	];
</script>

<Heading>
	Communicating Demo Resources to Backend API Service and handling access policies for identities.
</Heading>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
	{#each links as link (link.name)}
		<NavigationCard title={link.name} href={`backend-demo-resource${link.url}`}
			>{link.description}</NavigationCard
		>
	{/each}
</div>
