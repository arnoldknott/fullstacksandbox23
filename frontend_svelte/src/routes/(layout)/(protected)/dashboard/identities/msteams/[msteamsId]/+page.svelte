<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import IdentityAccordion from '../../IdentityAccordion.svelte';

	let { data }: { data: PageData } = $props();
</script>

<a href="../"
	><button class="btn btn-accent-container">
		<span class="icon-[tabler--chevron-left]"></span>
		Back to all identities
	</button></a
>

<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="">
	<IdentityAccordion
		icon="icon-[fluent--people-team-16-filled]"
		title={data.thisTeam.displayName || 'Unknown Team'}
		id={data.thisTeam.id || 'random_' + Math.random().toString(36).substring(2, 9)}
	>
		<JsonData data={data.thisTeam} />
	</IdentityAccordion>
</div>
