<script lang="ts">
	import type { PageData } from './$types';
	import { AccessHandler } from '$lib/accessHandler';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';
	import DemoResourceCard from './DemoResourceCard.svelte';
	import type { DemoResourceExtended, Identity } from '$lib/types';
	import { Action } from '$lib/accessHandler';
	let { data }: { data: PageData } = $props();
	let demoResources = $state(data.demoResourcesExtended);
	const microsoftTeams = data.microsoftTeams;

	let debug = $state(false);

	let identities: Identity[] = $derived.by(() => {
		const microsoftTeamsIdentities: Identity[] =
			AccessHandler.reduceMicrosoftTeamsToIdentities(microsoftTeams);
		// TBD add other identities here, e.g. from a ueber-group, group, sub-group, user list
		const emptyListAsPlaceholder: Identity[] = [];
		return [...microsoftTeamsIdentities, ...emptyListAsPlaceholder];
	});

	// This is the same as in +page.svelte  for socketIO!
	const addDemoResource = () => {
		const newResource: DemoResourceExtended = {
			id: 'new_' + Math.random().toString(36).substring(2, 9),
			name: '',
			access_right: Action.OWN,
			creation_date: new Date(Date.now())
		};
		demoResources.unshift(newResource);
	};
</script>

<!-- <code><pre>{JSON.stringify(demo_resources, null, ' ')}</pre></code> -->

<div class="mb-2 flex items-center gap-1">
	<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
	<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
</div>
<div class="mb-5">
	<button
		class="btn-neutral-container btn btn-gradient rounded-full"
		onclick={() => addDemoResource()}
		aria-label="Add Button"
	>
		<span class="icon-[fa6-solid--plus]"></span> Add
	</button>
</div>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-2" id="demoResourcesContainer">
	{#each demoResources as demoResource (demoResource.id)}
		<DemoResourceCard {demoResource} {identities} />
		<div class={debug ? 'block' : 'hidden'}>
			<Heading>{demoResource.name}</Heading>
			<p class="title-small md:title text-secondary">=> demoResource</p>
			<JsonData data={demoResource} />
		</div>
	{/each}
</div>
