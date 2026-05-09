<script lang="ts">
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	import Card from '$components/Card.svelte';
	import IdBadge from '../../../(protected)/IdBadge.svelte';
	// import
	import { SocketIO } from '$lib/socketio.svelte';
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import type { Presentation, PresentationExtended } from '$lib/types';
	import Display from '$components/Display.svelte';
	import { page } from '$app/state';
	import FormElement from '../../FormElement.svelte';

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

	const newPresentation = $state<Presentation>({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		source: '',
		path: ''
	});
</script>

{#snippet newPresentationHeader()}
	<Heading id="newPresentation">Add a presentation</Heading>
{/snippet}

<Display id="overview-presentations">Presentations</Display>

<Card id={newPresentation.id} header={newPresentationHeader}>
	<dl>
		<dt>
			<div class="label label-large">Slug</div>
			<p class="text-content-variant ml-5">
				This is the endpoint added for user access. It is not mandatory, as the presentation is
				always accessible via its id in place of the slug. <span class="text-accent"
					>Add a few words on allowed characters and uniqueness.</span
				>
			</p>
		</dt>
		<dd class="flex-cols-2 mx-5 mb-5 flex gap-2">
			<code class="mt-5 shrink">{page.url.origin}/presentation/</code>
			<div class="input-filled input-accent w-full">
				<input
					type="text"
					placeholder=""
					class="input"
					id="slugInput"
					bind:value={newPresentation.path}
				/>
				<label class="input-filled-label" for="slugInput"
					>[add the path to your presentation here]</label
				>
			</div>
		</dd>
	</dl>

	<dl>
		<dt>
			<div class="label label-large">Source</div>
			<p class="text-content-variant ml-5">
				Where is the source code for this presentation stored? For example, intern - as part of the
				source code of the platform - a github or gitlab repository. <span class="text-accent"
					>Consider adding the option for a staging environemnt.</span
				>
			</p>
		</dt>
		<dd class="m-5">
			For now, all presentations are <IdBadge id="intern" />, e.g. hosted with the source code of
			this platform.
		</dd>
	</dl>
</Card>

{#snippet existingPresentationsHeader()}
	<Heading id="existingPresentations">Existing presentations</Heading>
{/snippet}
<Card id="existing-presenations" header={existingPresentationsHeader} extraClasses="mt-6">
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
							<input
								type="text"
								placeholder="... enter slug"
								class="input input-sm"
								id="slugInput"
							/>
							<label class="input-filled-label" for="slugInput">Path to presentation/...</label>
						</div>
					</td>
					<td></td>
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
</Card>
