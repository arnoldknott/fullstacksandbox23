<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';
	import IdentityAccordion from './IdentityAccordion.svelte';
	let { data }: { data: PageData } = $props();
</script>

<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="">
	{#if data.session?.userProfile}
		<IdentityAccordion title="My user Profile in this app" id={data.session.userProfile.id} open={false}>
			<JsonData data={data.session?.userProfile} />
		</IdentityAccordion>
	{/if}

	<Heading>Microsoft Teams associated with this fullstack sandbox application:</Heading>

	{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
		<IdentityAccordion title={microsoftTeam.displayName} id={microsoftTeam.id}>
			<JsonData data={microsoftTeam} />
		</IdentityAccordion>
	{/each}
</div>
