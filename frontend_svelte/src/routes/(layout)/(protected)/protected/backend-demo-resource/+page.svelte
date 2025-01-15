<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';
	import { mount } from 'svelte';
	import DemoResourceCard from './DemoResourceCard.svelte';
	import type { AccessPolicy, DemoResourceExtended, MicrosoftTeamBasicExtended } from '$lib/types';
	let { data }: { data: PageData } = $props();
	// console.log('=== page data in backend-demo-resource/page.svelte ===');
	// console.log(data);
	const demoResources = data.demoResourcesExtended;
	const microsoftTeams = data.microsoftTeams;

	let debug = $state(false);

	const microsoftTeamsExtendWithAccessPolicies = (microsoftTeams: MicrosoftTeamBasicExtended[], demoResource: DemoResourceExtended) => {
		return microsoftTeams.map((team: MicrosoftTeamBasicExtended) => {
			return {
				...team,
				access_policies: demoResource.access_policies?.filter((policy: AccessPolicy) => team.id === policy.identity_id)
			};
		});
	};
</script>

<!-- <code><pre>{JSON.stringify(demo_resources, null, ' ')}</pre></code> -->

<div class="mb-2 flex items-center gap-1">
	<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
	<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
</div>
<div class="mb-5">
	<button
		class="btn-neutral-container btn btn-circle btn-gradient"
		onclick={async () => {
			const container = document.getElementById('demoResourcesContainer')!;
			const firstDemoResource = container.childNodes[0];
			mount(DemoResourceCard, {
				target: container,
				anchor: firstDemoResource,
				props: { microsoftTeams: microsoftTeams }
			});
			const { HSDropdown } = await import('flyonui/flyonui.js');
			HSDropdown.autoInit();
		}}
		aria-label="Add Button"
	>
		<span class="icon-[fa6-solid--plus]"></span>
	</button>
</div>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-2" id="demoResourcesContainer">
	{#each demoResources as demoResource}
		<DemoResourceCard {demoResource} microsoftTeams={microsoftTeamsExtendWithAccessPolicies(microsoftTeams, demoResource)}/>
		<div class={debug ? 'block' : 'hidden'}>
			<Heading>{demoResource.name}</Heading>
			<p class="text-title-small md:text-title text-secondary">=> demoResource</p>
			<JsonData data={demoResource} />
			<p class="text-title-small md:text-title text-secondary">=> microsoftTeams</p>
			<JsonData data={microsoftTeamsExtendWithAccessPolicies(microsoftTeams, demoResource)} />
		</div>
	{/each}
</div>
