<script lang="ts">
	export const links = [
		{
			name: 'Components',
			url: '/components'
		},
		{
			name: 'Backend',
			url: '/backend'
		},
		{
			name: 'Counter',
			url: '/counter'
		},
		{
			name: 'User store',
			url: '/userstore'
		}
	];
</script>

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
</div>
