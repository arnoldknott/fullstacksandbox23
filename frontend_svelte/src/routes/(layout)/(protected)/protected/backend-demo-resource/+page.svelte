<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';
	import { mount } from 'svelte';
	import DemoResourceCard from './DemoResourceCard.svelte';
	let { data }: { data: PageData } = $props();
	const demoResources = data.demoResourcesWithCreationDates;
	const microsoftTeams = data.microsoftTeams;

	let debug = $state(false);
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
			mount(DemoResourceCard, { target: container, anchor: firstDemoResource });
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
		<DemoResourceCard {demoResource} {microsoftTeams} />
		<div class={debug ? 'block' : 'hidden'}>
			<Heading>{demoResource.name}</Heading>
			<JsonData data={demoResource} />
		</div>
	{/each}
</div>
