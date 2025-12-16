<script lang="ts">
	import { resolve } from '$app/paths';
	import NavigationCard from '$components/NavigationCard.svelte';

	const links = [
		{
			name: 'User interface',
			description: 'Playground for layouting navigation elements, components, and placements',
			url: resolve('/(layout)/playground/user-interface')
		},
		{
			name: 'Components',
			description:
				'Prototypes of components with applied design - candidates to become Svelte components',
			url: resolve('/(layout)/playground/components') + '?develop=true&prod=false'
		},
		{
			name: 'Design',
			description:
				'Design adaption of Material Design 3 principles to FlyonUI components supported by TailwindCSS',
			url: resolve('/(layout)/playground/design')
		},
		{
			name: 'Data Flow & Navigation',
			description:
				'Playground for data flow in Svelte from server to browser via load functions and page data and from browser to server via form data as well as error and redirect navigation.',
			url: resolve('/(layout)/playground/dataflow')
		},
		{
			name: 'Backend - Schema',
			description: 'The openapi schema of the backend API',
			url: resolve('/(layout)/playground/backend-schema')
		},
		{
			name: 'Counter',
			description:
				'A simple counter, stored in a svelte store. Works well to try  page reloads: the counter gets reset every time.',
			url: resolve('/(layout)/playground/counter')
		},
		{
			name: 'Core',
			description:
				'Core data of the application: host names, connection to the keyvault through the backend API, etc.',
			url: resolve('/(layout)/playground/core')
		},
		{
			name: 'UserAgent',
			description: 'TBD: UserAgent data of the application: browser, OS, etc.',
			url: resolve('/(layout)/playground/user-agent')
		},
		{
			name: 'Websockets',
			description: 'Establishing various websocket connections to backend and using them',
			url: resolve('/(layout)/playground/websockets')
		}
	];
</script>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
	{#each links as link (link.name)}
		<NavigationCard title={link.name} href={link.url}>{link.description}</NavigationCard>
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
