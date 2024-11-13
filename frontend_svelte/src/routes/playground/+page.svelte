<script lang="ts">
	import Card from '$components/Card.svelte';

	export const links = [
		{
			name: 'Components',
			description:
				'Svelte components to play around with various Tailwind CSS features and Tailwind elements',
			url: '/components'
		},
		{
			name: 'Backend - Schema',
			description: 'The openapi schema of the backend API',
			url: '/backend_schema'
		},
		{
			// TBD: don't do "_" in URLs, ideally just "/", but "-" is also ok.
			name: 'Backend - Demo Resources',
			description:
				'The demo resources of the backend API, retrieved through the backend API from the postgres database',
			url: '/backend_demo_resource'
		},
		{
			name: 'Microsoft Graph - Me',
			description: 'The Microsoft Graph API - Me endpoint, all data in json',
			url: '/ms_graph_me'
		},
		{
			name: 'Counter',
			description:
				'A simple counter, stored in a svelte store. Works well to try  page reloads: the counter gets reset every time.',
			url: '/counter'
		},
		{
			name: 'User store',
			description:
				'A simple user store, stored in a svelte store: contains json data of the logged in user',
			url: '/userstore'
		},
		{
			name: 'Core',
			description:
				'Core data of the application: host names, connection to the keyvault through the backend API, etc.',
			url: '/core'
		},
		{
			name: 'UserAgent',
			description: 'TBD: UserAgent data of the application: browser, OS, etc.',
			url: '/user_agent'
		},
		{
			name: 'On behalf of user acceess',
			description: 'TBD: On behalf of user access to the Microsoft Graph API',
			url: '/onbehalfof'
		},
		{
			name: 'User interface',
			description: 'play with elements of the user interface',
			url: '/user_interface'
		},
		{
			name: 'Websockets',
			description: 'Establishing various websocket connections to backend and using them',
			url: '/websockets'
		},
		{
			name: 'Socket.IO',
			description: 'Establishing various Socket.IO connections to backend and using them',
			url: '/socketio'
		}
	];
</script>

Version 3:

<div class="grid grid-cols-3 gap-4">
	{#each links as link}
		<div>
			<Card title={link.name} description={link.description} href={`playground${link.url}`}></Card>
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
