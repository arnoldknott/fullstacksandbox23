<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import IdentityAccordion from './IdentityAccordion.svelte';
	let { data }: { data: PageData } = $props();
</script>

<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="">
	{#if data.session?.userProfile}
		<IdentityAccordion
			title="My user Profile in this app"
			id={data.session.userProfile.id}
			open={false}
		>
			<JsonData data={data.session?.userProfile} />
		</IdentityAccordion>
	{/if}

	<div class="title-large m-2">
		Microsoft Teams associated with this fullstack sandbox application:
	</div>

	{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
		<IdentityAccordion
			icon="icon-[fluent--people-team-16-filled]"
			title={microsoftTeam.displayName || 'Unknown Team'}
			id={microsoftTeam.id || 'random_' + Math.random().toString(36).substring(2, 9)}
		>
			<div class="badge badge-secondary-container">{microsoftTeam.id}</div>

			<p class="body bg-primary text-primary-content">{microsoftTeam.description}</p>
			<a href={microsoftTeam.webUrl} target="_blank" rel="noopener"
				><button class="btn btn-primary-container">Open in Microsoft Teams</button></a
			>
			<a href="./identities/msteams/{microsoftTeam.id}"
				><button class="btn btn-accent-container">More information</button></a
			>
		</IdentityAccordion>
	{/each}
	{#each data.ueberGroups as uberGroup (uberGroup.id)}
		<IdentityAccordion
			icon="icon-[fa--institution]"
			title={uberGroup.name || 'Unknown Group'}
			id={uberGroup.id}
		>
			<div class="badge badge-secondary-container">{uberGroup.id}</div>

			<p class="body bg-primary text-primary-content">{uberGroup.description}</p>
			<a href="./identities/ueber-group/{uberGroup.id}"
				><button class="btn btn-accent-container">More information</button></a
			>
		</IdentityAccordion>
	{/each}
</div>
