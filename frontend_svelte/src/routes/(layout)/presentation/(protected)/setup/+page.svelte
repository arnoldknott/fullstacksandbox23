<script lang="ts">
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	import IdBadge from '../../../(protected)/IdBadge.svelte';
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
<div class="w-full overflow-x-auto">
	<table class="table">
		<thead>
			<tr>
				<th>Link</th>
				<th>Slug / Id</th>
				<th>Source</th>
				<th>Access</th>
				<th>Actions</th>
				<th># Questions</th>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td><span class="icon-[clarity--new-solid] bg-accent size-9"></span></td>
				<td>
					<div class="input-filled input-accent w-full grow">
						<input type="text" placeholder="... enter slug" class="input input-sm" id="slugInput" />
						<label class="input-filled-label" for="slugInput">Path to presentation/...</label>
					</div>
				</td>
				<td><IdBadge id="intern" /></td>
				<td
					><div class="flex items-center gap-1">
						<input type="checkbox" class="checkbox checkbox-accent" id="checkboxPublic" checked />
						<label class="label-text text-base" for="checkboxPublic"
							><span class="icon-[gis--globe-earth-alt] size-6"></span>Public</label
						>
					</div></td
				>
				<td>
					<button
						class="btn-success-container btn btn-circle btn-gradient shadow-outline shadow-sm"
						aria-label="Send"
					>
						<!-- onclick={() => {
								socketio.submitEntity(newPresentation);
								newPresentation.id = 'new_' + Math.random().toString(36).substring(2, 9);
								newPresentation.slug = '';
								newPresentation.source = [];
								newPresentation.public = true;
							}} -->
						<span class="icon-[tabler--send-2]"></span>
					</button></td
				>
			</tr>
			{#if (socketioPresentations?.entities?.length ?? 0) === 0}
				<tr>
					<td colspan={6} class="text-center">
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
