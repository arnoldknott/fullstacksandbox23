<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	import { Action } from '$lib/accessHandler';
	import type { DemoResourceExtended } from '$lib/types';

	import type { PageData } from './$types';
	import DemoResourceCard from './DemoResourceCard.svelte';
	let { data }: { data: PageData } = $props();
	// svelte-ignore state_referenced_locally
	let demoResources = $state(data.payload.demoResources);
	const identities = $derived(data.payload.identities);

	let debug = $state(false);

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
		class="btn-neutral-container btn btn-gradient shadow-outline rounded-full shadow-sm"
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
			<Title id={'debug-title-' + demoResource.id}>{demoResource.name}</Title>
			<p class="title-small md:title text-secondary">=> demoResource</p>
			<JsonData data={demoResource} />
		</div>
	{/each}
</div>
