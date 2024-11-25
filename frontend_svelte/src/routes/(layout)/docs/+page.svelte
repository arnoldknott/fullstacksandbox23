<script lang="ts">
	import Presentation from '$components/Presentation.svelte';
	export const ssr = false;
</script>

<div class="grid grid-cols-1 gap-4 p-4">
	<Presentation title="Overview">
		<iframe title="Overview" src="/docs/overview" width="100%" height="400px"></iframe>
	</Presentation>
</div>

<div class="grid grid-cols-2 gap-4 p-4">
	<Presentation title="GitHub - CI/CD">GitHub - CI/CD</Presentation>
	<Presentation>Infrastructure - Cloud: Azure</Presentation>
	<Presentation>Architecture - Containers: Docker</Presentation>
	<Presentation>Environments: dev - test - stage - prod</Presentation>
	<Presentation>Security: OAuth2 - AccessControl - Logging</Presentation>
	<Presentation>Backend: REST API, Socket.io server, websockets</Presentation>
	<Presentation>Frontend: Svelte, Material Design, TailwindCSS, Reveal.JS</Presentation>
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
