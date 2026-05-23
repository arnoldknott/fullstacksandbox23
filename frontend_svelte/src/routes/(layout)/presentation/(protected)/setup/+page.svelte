<script lang="ts">
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	import Card from '$components/Card.svelte';
	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import { AccessHandler, Action, IdentityType } from '$lib/accessHandler';
	import { SocketIO } from '$lib/socketio.svelte';
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import type { AccessShareOption, Presentation, PresentationExtended } from '$lib/types';
	import Display from '$components/Display.svelte';
	import { page } from '$app/state';
	import FormElement from './FormElement.svelte';
	import ShareItem from '../../../playground/components/ShareItem.svelte';

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

	const shareOptions: AccessShareOption[] = $state([
		{
			identity_id: 'public',
			identity_name: 'Public',
			identity_type: IdentityType.PUBLIC,
			action: Action.READ,
			public: true
		},
		{
			identity_id: 'some-group-id',
			identity_name: 'Some Group Name',
			identity_type: IdentityType.GROUP,
			action: Action.WRITE
		},
		{
			identity_id: 'some-teams-id',
			identity_name: 'A Microsoft Team',
			identity_type: IdentityType.MICROSOFT_TEAM
		},
		{
			identity_id: 'Ueber Group 1',
			identity_name: 'Some complete University',
			identity_type: IdentityType.UEBER_GROUP
		},
		{
			identity_id: 'Ueber Group 2',
			identity_name: 'A big School',
			identity_type: IdentityType.UEBER_GROUP
		}
	]);

	// For showing existing presentations:
	let viewMode = $state<'preview' | 'grid' | 'list'>('list');
</script>

{#snippet newPresentationHeader()}
	<Heading id="newPresentation">Add a presentation</Heading>
{/snippet}

<Display id="overview-presentations">Presentations</Display>

{#snippet slugDescription()}
	This is the endpoint added for user access. It is not mandatory, as the presentation is always
	accessible via its id in place of the slug. <span class="text-accent"
		>Add a few words on allowed characters and uniqueness.</span
	>
{/snippet}

{#snippet sourceDescription()}
	Where is the source code for this presentation stored? For example, intern - as part of the source
	code of this platform - a github or gitlab repository. <span class="text-accent"
		>Consider adding the option for a staging environemnt.</span
	>
{/snippet}

{#snippet accessDescription()}
	Who has which access to this presentation?
	<br />
	Default is public <span class="icon-[gis--globe-earth-alt] size-4"></span>
	and have read
	<span
		class={`${AccessHandler.rightsIcon(Action.READ)} ${AccessHandler.rightsIconColor(Action.READ)} size-4`}
	></span>
	access.
{/snippet}

<Card id={newPresentation.id} header={newPresentationHeader}>
	<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
		<FormElement title="Slug" description={slugDescription} classes="col-span-2">
			<div class="flex-cols-2 flex gap-2">
				<code class="mt-5 shrink">{page.url.origin}/presentation/</code>
				<div class="input-filled input-primary w-full">
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
			</div>
		</FormElement>

		<FormElement title="Access" description={accessDescription} classes="row-span-2">
			<ul
				class="bg-base-150 shadow-outline max-h-48 max-w-fit overflow-y-auto rounded-lg p-2 shadow-inner"
			>
				{#each shareOptions as shareOption, i (i)}
					<ShareItem
						resourceId={newPresentation.id}
						share={(policy) => {
							shareOption.action = policy.new_action;
						}}
						{shareOption}
						wide
					/>
				{/each}
			</ul>
		</FormElement>

		<FormElement title="Source" description={sourceDescription}>
			For now, all presentations are <IdBadge id="intern" />, e.g. hosted with the source code of
			this platform.
		</FormElement>
	</div>
</Card>

{#snippet existingPresentationsHeader()}
	<div class="flex justify-between">
		<Heading id="existingPresentations">Existing presentations</Heading>
		<div class="join flex flex-row items-center justify-center rounded-lg">
			<button
				aria-label="Preview"
				class="btn join-item btn-secondary py-4 {viewMode !== 'preview' ? 'opacity-60' : ''}"
				onclick={() => (viewMode = 'preview')}
			>
				<span class="icon-[material-symbols-light--preview-outline] size-6"></span>
			</button>
			<button
				aria-label="Grid"
				class="btn join-item btn-secondary py-4 {viewMode !== 'grid' ? 'opacity-60' : ''}"
				onclick={() => (viewMode = 'grid')}
			>
				<span class="icon-[gridicons--grid] size-6"></span>
			</button>
			<button
				aria-label="List"
				class="btn join-item btn btn-secondary py-4 {viewMode !== 'list' ? 'opacity-60' : ''}"
				onclick={() => (viewMode = 'list')}
			>
				<span class="icon-[material-symbols-light--table-outline] size-6"></span>
			</button>
		</div>
	</div>
{/snippet}
<Card id="existing-presenations" header={existingPresentationsHeader} extraClasses="mt-6">
	<div class="w-full overflow-x-auto {viewMode !== 'preview' ? 'hidden' : ''}">
		<p class="bg-warning text-warning-content rounded-lg p-4">Preview mode is not developed yet</p>
	</div>
	<div class="w-full overflow-x-auto {viewMode !== 'grid' ? 'hidden' : ''}">
		<p class="bg-warning text-warning-content rounded-lg p-4">
			Grid view mode is not developed yet
		</p>
	</div>
	<div class="w-full overflow-x-auto {viewMode !== 'list' ? 'hidden' : ''}">
		<table class="table w-full">
			<thead>
				<tr>
					<th>Link</th>
					<th>Slug / Id</th>
					<th>Source</th>
					<th>Access</th>
					<th># <span class="icon-[codicon--question]"></span></th>
					<th># <span class="icon-[line-md--link]"></span></th>
					<th># <span class="icon-[tabler--file]"></span></th>
					<th><span class="icon-[fluent-mdl2--offline-storage]"></span></th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
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
							<td>[Access]</td>
							<td>[Number]</td>
							<td>[Number]</td>
							<td>[Number]</td>
							<td>[Mb / Gb]</td>
							<td>[edit/delete]</td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</Card>
