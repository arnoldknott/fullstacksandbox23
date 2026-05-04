<script lang="ts">
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import type { PresentationExtended } from '$lib/types';

	let { data }: { data: PageData } = $props();

	let socketioPresentations: SocketIO<PresentationExtended> = $state()!;
	onMount(() => {
		socketioPresentations = new SocketIO(
			{
				namespace: '/presentation',
				cookie_session_id: data?.session?.sessionId || '',
				query_params: { 'request-access-data': true }
			},
			{
				subscribeEntities: () => data.payload.presentations || []
			}
		);
	});
</script>

<Heading id="overview-presentations">Presentations</Heading>
<div>
	<p>Add a presentation here!</p>
</div>
<div class="w-full overflow-x-auto">
	<table class="table">
		<thead>
			<tr>
				<th></th>
				<th>Slug</th>
				<th>Source</th>
				<th>Id</th>
			</tr>
		</thead>
		<tbody>
			{#if (socketioPresentations?.entities?.length ?? 0) === 0}
				<tr>
					<td colspan={4} class="text-center">
						No presentations yet. Create one by sending a POST request to the /presentation
						endpoint.
					</td>
				</tr>
			{:else}
				{#each socketioPresentations.entities as presentation (presentation.id)}
					<tr>
						<td
							><a
								href={resolve('/(layout)/presentation/(protected)/setup/[id]', {
									id: presentation.path || presentation.id
								})}
								aria-label={`Setup presentation ${presentation.path || presentation.id}`}
								><button
									type="button"
									class="btn btn-info-container btn-gradient shadow-outline btn-circle shadow-sm"
									aria-label={`Setup presentation ${presentation.path || presentation.id}`}
								>
									<span class="icon-[mingcute--arrow-right-fill] size-4"></span>
								</button></a
							></td
						>
						<td>{presentation.path}</td>
						<td>{presentation.source}</td>
						<td>{presentation.id}</td>
					</tr>
				{/each}
			{/if}
		</tbody>
	</table>
</div>
<!-- <JsonData {data} /> -->
