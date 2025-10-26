<!-- Rename the folder of this file "protected" into the real content -->

<script lang="ts">
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	import { page } from '$app/state';
	import NavigationCard from '$components/NavigationCard.svelte';

	const resources = [
		{
			// TBD: don't do "_" in URLs, ideally just "/", but "-" is also ok.
			name: 'Backend - Demo Resources',
			description:
				'The demo resources of the backend API, retrieved through the backend API from the postgres database',
			url: '/backend-demo-resource'
		},
		{
			name: 'Protected Hierarchy',
			description:
				'The protected hierarchy family consisting of protected resource, protected child and protected grandchild',
			url: '/backend-protected-hierarchy'
		}
	];
	const identities = [
		{
			name: 'All Identities',
			description:
				'Identities: various kinds of groups and relationship to users from the backend API',
			url: '/identities'
		},
		{
			name: 'Microsoft Graph',
			description: 'The Microsoft Graph API endpoint, all data in json',
			url: '/msgraph'
		}
	];
	const services = [
		{
			name: 'Socket.IO',
			description: 'Establishing various Socket.IO connections to backend and using them',
			url: '/socketio'
		}
	];
	const application = [
		{
			name: 'Session data',
			description:
				'Session data including userprofile stores in $page data: contains json data of the logged in user',
			url: '/sessiondata'
		},
		{
			name: 'On behalf of user acceess',
			description: 'TBD: On behalf of user access to the Microsoft Graph API',
			url: '/onbehalfof'
		}
	];
</script>

<Display>
	{page.data.session.microsoftProfile.displayName}'s Dashboard
</Display>

<Heading id="resources">Resources</Heading>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
	{#each resources as resource (resource.name)}
		<NavigationCard title={resource.name} href={`dashboard${resource.url}`}
			>{resource.description}</NavigationCard
		>
	{/each}
</div>

<Heading id="identities">Identities</Heading>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
	{#each identities as identity (identity.name)}
		<NavigationCard title={identity.name} href={`dashboard${identity.url}`}
			>{identity.description}</NavigationCard
		>
	{/each}
</div>

<Heading id="services">Services</Heading>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
	{#each services as service (service.name)}
		<NavigationCard title={service.name} href={`dashboard${service.url}`}
			>{service.description}</NavigationCard
		>
	{/each}
</div>

<Heading id="application">Application Data</Heading>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
	{#each application as app (app.name)}
		<NavigationCard title={app.name} href={`dashboard${app.url}`}>{app.description}</NavigationCard>
	{/each}
</div>
