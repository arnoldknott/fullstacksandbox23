<script lang="ts">
	import Card from '$components/Card.svelte';

	export const links = [
		{
			// TBD: don't do "_" in URLs, ideally just "/", but "-" is also ok.
			name: 'Backend - Demo Resources',
			description:
				'The demo resources of the backend API, retrieved through the backend API from the postgres database',
			url: '/backend-demo-resource'
		},
		{
			name: 'Microsoft Graph',
			description: 'The Microsoft Graph API endpoint, all data in json',
			url: '/msgraph'
		},
		{
			name: 'Socket.IO',
			description: 'Establishing various Socket.IO connections to backend and using them',
			url: '/socketio'
		},
		{
			name: 'Protected Hierarchy',
			description: 'The protected hierarchy family consisting of protected resource, protected child and protected grandchild',
			url: '/backend-protected-hierarchy'
		},
		{
			name: 'Session data',
			description:
				'Session data including userprofile stores in $page data: contains json data of the logged in user',
			url: '/sessiondata'
		},
		{
			name: 'Application Roles',
			description: 'User signup for application roles',
			url: '/approles'
		},
		{
			name: 'On behalf of user acceess',
			description: 'TBD: On behalf of user access to the Microsoft Graph API',
			url: '/onbehalfof'
		},

	];
</script>

Version 3:

<div class="grid grid-cols-3 gap-4">
	{#each links as link}
		<div>
			<Card title={link.name} description={link.description} href={`protected${link.url}`}></Card>
		</div>
	{/each}
</div>

<!-- Version 2:

<div class="grid grid-cols-3 gap-4">

	{#each links as link}
		<div>
			<li>
				<a
					class="text-xl text-blue-400 transition duration-150 ease-in-out hover:text-neutral-600 focus:text-neutral-700 active:text-neutral-300"
					href={`/playground${link.url}`}
				>
					{link.name}
				</a>
			</li>
		</div>
	{/each}

</div>

Version 1:

<div class="mx-5">
	<ul>
		{#each links as link}
			<li>
			<a
					class="text-xl text-blue-400 transition duration-150 ease-in-out hover:text-neutral-600 focus:text-neutral-700 active:text-neutral-300"
					href={`/playground${link.url}`}
				>
					{link.name}
				</a>
			</li>
		{/each}
	</ul>
</div> -->
