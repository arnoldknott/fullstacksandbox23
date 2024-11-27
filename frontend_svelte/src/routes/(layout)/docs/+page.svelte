<script lang="ts">
	import Presentation from '$components/Presentation.svelte';
	export const ssr = false;

	const presentations = [
		{
			title: 'Repository',
			link: '/docs/repository'
		},
		{
			title: 'Infrastructure',
			link: '/docs/infrastructure'
		},
		{
			title: 'Architecture',
			link: '/docs/architecture'
		},
		// {
		//     title: "Environments",
		//     link: "/docs/environments"
		// },
		{
			title: 'Security',
			link: '/docs/security'
		},
		{
			title: 'Backend',
			link: '/docs/backend'
		},
		{
			title: 'Frontend',
			link: '/docs/frontend'
		}
	];
</script>

<div class="grid grid-cols-1 gap-4 p-4">
	<Presentation title="Overview" link="/docs/overview">
		<iframe title="Overview" src="/docs/overview" width="100%" height="400px"></iframe>
	</Presentation>
</div>

<div class="grid grid-cols-2 gap-4 p-4">
	{#each presentations as { title, link }}
		<Presentation title={title} link={link}>
			<iframe {title} src={link} width="100%" height="400px"></iframe>
		</Presentation>
	{/each}
</div>

<!-- <div>
    <div class="w-80">
        <Presentation>
            <a href="http://localhost:8661/docs/overview"><iframe src="http://localhost:8661/docs/overview"></iframe></a>
        </Presentation>
    </div>
    <div class="grid grid-cols-2 gap-4">
        <Presentation>
            GitHub - CI/CD
        </Presentation>
        <Presentation>
            Infrastructure - Cloud: Azure
        </Presentation>
        <Presentation>
            Architecture - Containers: Docker
        </Presentation>
        <Presentation>
            Environments: dev - test - stage - prod
        </Presentation>
        <Presentation>
            Security: OAuth2 - AccessControl - Logging
        </Presentation>
        <Presentation>
            Backend: REST API, Socket.io server, websockets
        </Presentation>
        <Presentation>
            Frontend: Svelte, Material Design, TailwindCSS, Reveal.JS
        </Presentation>
    </div>
</div> -->
