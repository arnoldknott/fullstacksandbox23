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

	{#if data.microsoftTeams.length === 0}
		<div class="alert alert-warning label-large text-center" role="alert">
			No Microsoft Teams found for this user.
		</div>
	{/if}

	{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
		<IdentityAccordion
			icon="icon-[fluent--people-team-16-filled]"
			title={microsoftTeam.displayName || 'Unknown Team'}
			id={microsoftTeam.id || 'random_' + Math.random().toString(36).substring(2, 9)}
		>
			<p class="body">{microsoftTeam.description}</p>
			<a href={microsoftTeam.webUrl} target="_blank" rel="noopener"
				><button class="btn btn-primary-container"
					><span class="icon-[bi--microsoft-teams]"></span>Open in Microsoft Teams</button
				></a
			>
			<a href="./identities/msteams/{microsoftTeam.id}"
				><button class="btn btn-info-container"
					><span class="icon-[tabler--info-triangle]"></span>More information</button
				></a
			>
			{#if debug}
				<JsonData data={microsoftTeam} />
			{/if}
		</IdentityAccordion>
	{/each}

	<div class="flex w-full flex-row">
		<div class="grow">
			<div class="title-large m-2">
				Ueber-Groups associated with this fullstack sandbox application,
			</div>
			<div class="title-small m-2">
				that {data.session?.microsoftProfile?.displayName || 'current user'} is a member of:
			</div>
		</div>
		{#if data.session?.currentUser?.azure_token_roles?.find((roles) => roles === 'Admin')}
			<button class="btn-warning-container btn mr-2 self-center" aria-label="Create Ueber Group">
				<span class="icon-[material-symbols--edit-outline-rounded]"></span> Create Ueber Group
			</button>
		{/if}
	</div>

	{#if data.ueberGroups.length === 0}
		<div class="alert alert-warning label-large text-center" role="alert">
			No Ueber-Groups found for this user.
		</div>
	{/if}

	{#each data.ueberGroups as uberGroup (uberGroup.id)}
		<IdentityAccordion
			icon="icon-[fa--institution]"
			title={uberGroup.name || 'Unknown Group'}
			id={uberGroup.id}
		>
			<div class="flex gap-2">
				<div class="flex flex-col">
					<p class="body">{uberGroup.description}</p>
					<div class="flex gap-2">
						<a href="./identities/ueber-group/{uberGroup.id}"
							><button class="btn btn-info-container"
								><span class="icon-[tabler--info-triangle]"></span>More information</button
							></a
						>
						<button class="btn btn-accent-container"
							><span class="icon-[fa6-solid--plus]"></span> Add Group</button
						>
						<button class="btn btn-accent-container"
							><span class="icon-[fa6-solid--plus]"></span> Add User</button
						>
					</div>
				</div>
				{#if debug}
					<JsonData data={uberGroup} />
				{/if}
			</div>
		</IdentityAccordion>
	{/each}
</div>
