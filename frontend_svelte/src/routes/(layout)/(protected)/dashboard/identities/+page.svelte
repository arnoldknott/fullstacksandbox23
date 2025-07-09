<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	import JsonData from '$components/JsonData.svelte';
	import IdentityAccordion from './IdentityAccordion.svelte';
	let { data }: { data: PageData } = $props();

	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		if (debug) {
			goto(`?debug=true`, { replaceState: true });
		} else {
			goto(`?`, { replaceState: true });
		}
	});
</script>

<div>
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
		<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
	</div>
</div>

<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="">
	{#if data.session?.currentUser}
		<IdentityAccordion
			title="My user Profile in this app"
			id={data.session.currentUser.id}
			open={false}
		>
			<JsonData data={data.session?.currentUser} />
		</IdentityAccordion>
	{/if}

	<div>
		<div class="title-large m-2">
			Microsoft Teams associated with this fullstack sandbox application
		</div>
		<div class="title-small m-2">
			that {data.session?.microsoftProfile?.displayName || 'current user'} is a member of:
		</div>
	</div>

	{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
		<IdentityAccordion
			icon="icon-[fluent--people-team-16-filled]"
			title={microsoftTeam.displayName || 'Unknown Team'}
			id={microsoftTeam.id || 'random_' + Math.random().toString(36).substring(2, 9)}
		>
			<div class="badge badge-secondary-container">{microsoftTeam.id}</div>

			<p class="body">{microsoftTeam.description}</p>
			<a href={microsoftTeam.webUrl} target="_blank" rel="noopener"
				><button class="btn btn-primary-container">Open in Microsoft Teams</button></a
			>
			<a href="./identities/msteams/{microsoftTeam.id}"
				><button class="btn btn-accent-container">More information</button></a
			>
			{#if debug}
				<JsonData data={microsoftTeam} />
			{/if}
		</IdentityAccordion>
	{/each}

	<div>
		<div class="title-large m-2">
			Ueber Groups associated with this fullstack sandbox application,
		</div>
		<div class="title-small m-2">
			that {data.session?.microsoftProfile?.displayName || 'current user'} is a member of:
		</div>
	</div>

	{#if data.session?.currentUser?.ueber_groups?.length === 0}
		<p class="body">No Ueber Groups found for this user.</p>
	{/if}

	{#each data.ueberGroups as uberGroup (uberGroup.id)}
		<IdentityAccordion
			icon="icon-[fa--institution]"
			title={uberGroup.name || 'Unknown Group'}
			id={uberGroup.id}
		>
			<div class="badge badge-secondary-container">{uberGroup.id}</div>

			<p class="body">{uberGroup.description}</p>
			<a href="./identities/ueber-group/{uberGroup.id}"
				><button class="btn btn-accent-container">More information</button></a
			>
			{#if debug}
				<JsonData data={uberGroup} />
			{/if}
		</IdentityAccordion>
	{/each}
</div>
