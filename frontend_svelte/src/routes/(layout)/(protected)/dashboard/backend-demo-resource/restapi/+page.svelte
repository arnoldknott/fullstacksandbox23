<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';
	import { mount } from 'svelte';
	import DemoResourceCard from './DemoResourceCard.svelte';
	import type { AccessShareOption, DemoResourceExtended, MicrosoftTeamExtended } from '$lib/types';
	import { AccessHandler, IdentityType } from '$lib/accessHandler';
	let { data }: { data: PageData } = $props();
	// console.log('=== page data in backend-demo-resource/page.svelte ===');
	// console.log(data);
	let demoResources = $state(data.demoResourcesExtended);
	const microsoftTeams = data.microsoftTeams;

	let debug = $state(false);

	// const shareOptions: AccessShareOption[] = $derived.by(() => {
	// 	return demoResources
	// 		.flatMap((demoResource: DemoResourceExtended) => {
	// 			microsoftTeams
	// 				.filter((team: MicrosoftTeamExtended) => team.id)
	// 				.map((team: MicrosoftTeamExtended) => {
	// 					return {
	// 						identity_id: team.id,
	// 						identity_name: team.displayName || 'Unknown Team',
	// 						identity_type: IdentityType.MICROSOFT_TEAM,
	// 						action: AccessHandler.getRights(team.id, demoResource.access_policies),
	// 						public: false
	// 					};
	// 				})
	// 		)
	// 		.sort((a: AccessShareOption, b: AccessShareOption) => {
	// 			return a.identity_type - b.identity_type || a.identity_name.localeCompare(b.identity_name);
	// 		});
	// });

	// TBD: consider moving this to server side:
	demoResources.forEach((demoResource: DemoResourceExtended) => {
		demoResource.access_share_options = microsoftTeams
			.filter((team: MicrosoftTeamExtended) => team.id !== undefined)
			.map((team: MicrosoftTeamExtended) => {
				return {
					identity_id: team.id as string,
					identity_name: team.displayName || 'Unknown Team',
					identity_type: IdentityType.MICROSOFT_TEAM,
					action: AccessHandler.getRights(team.id, demoResource.access_policies),
					public: false
				};
			})
			.sort((a: AccessShareOption, b: AccessShareOption) => {
				return a.identity_type - b.identity_type || a.identity_name.localeCompare(b.identity_name);
			});
	});

	// $effect(() => {
	// 	console.log('=== shareOptions ===');
	// 	console.log(shareOptions);
	// });
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
			// TBD: refactor into adding an element to the demoResources array
			mount(DemoResourceCard, {
				target: container,
				anchor: firstDemoResource,
				// props: { shareOptions: shareOptions }
			});
			// TBD: refactor into using an attachment:
			const { HSDropdown } = await import('flyonui/flyonui.js');
			HSDropdown.autoInit();
		}}
		aria-label="Add Button"
	>
		<span class="icon-[fa6-solid--plus]"></span>
	</button>
</div>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-2" id="demoResourcesContainer">
	{#each demoResources as demoResource (demoResource.id)}
		<DemoResourceCard {demoResource} />
		<div class={debug ? 'block' : 'hidden'}>
			<Heading>{demoResource.name}</Heading>
			<p class="title-small md:title text-secondary">=> demoResource</p>
			<JsonData data={demoResource} />
		</div>
	{/each}
</div>
