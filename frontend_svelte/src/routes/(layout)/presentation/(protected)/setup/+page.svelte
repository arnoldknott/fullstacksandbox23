<script lang="ts">
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	import Card from '$components/Card.svelte';
	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import { AccessHandler, Action, IdentityType } from '$lib/accessHandler';
	import { SocketIO } from '$lib/socketio.svelte';
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import type { AccessShareOption, PresentationExtended } from '$lib/types';
	import Display from '$components/Display.svelte';
	import { page } from '$app/state';
	import FormElement from './FormElement.svelte';
	import ShareItem from '../../../playground/components/ShareItem.svelte';
	import { initDropdown } from '$lib/userInterface';

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

	const createNewPresentation = (): PresentationExtended => {
		return {
			id: 'new_' + Math.random().toString(36).substring(2, 9),
			source: 'intern:',
			path: '',
			access_right: Action.OWN,
			creation_date: new Date(Date.now())
		};
	};
	let newPresentation = $state<PresentationExtended>(createNewPresentation());

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

	let actionButtonShareMenu: HTMLElement;
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
	<div class="flex w-full flex-wrap gap-6">
		<div class="grow">
			<FormElement title="Slug" description={slugDescription}>
				<div class="md:flex-cols-2 wrap flex gap-2">
					<code class="mt-5 shrink">{page.url.origin}/presentation/</code>
					<div class="input-filled input-primary w-full">
						<input
							type="text"
							placeholder=""
							class="input"
							id="slugInput"
							bind:value={newPresentation.path}
							onblur={() => {
								const newPath = newPresentation?.path?.trim() ?? '';
								newPresentation.path =
									newPath && !newPath.startsWith('/') ? `/${newPath}` : newPath;
								socketioPresentations?.submitEntity(newPresentation);
								socketioPresentations?.addEntity(newPresentation);
								newPresentation = createNewPresentation();
							}}
						/>
						<label class="input-filled-label" for="slugInput"
							>[add the path to your presentation here]</label
						>
					</div>
				</div>
			</FormElement>
			<FormElement title="Source" description={sourceDescription}>
				For now, all presentations are <IdBadge id="intern" />, e.g. hosted with the source code of
				this platform.
			</FormElement>
		</div>

		<FormElement title="Access" description={accessDescription}>
			<ul
				class="bg-base-150 shadow-outline max-h-48 max-w-fit overflow-y-auto rounded-lg p-2 shadow-inner"
			>
				{#each shareOptions as shareOption, i (i)}
					<ShareItem
						resourceId={newPresentation.id}
						{shareOption}
						share={socketioPresentations?.shareEntity.bind(socketioPresentations)}
						wide
					/>
				{/each}
			</ul>
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

{#snippet actionButtons(resourceId: string)}
	<div class="join flex flex-row items-center justify-center">
		<button
			class="btn btn-secondary-container text-secondary-container-content join-item grow"
			aria-label="Edit Button"
			onclick={() => console.log('Edit', resourceId)}
		>
			<span class="icon-[material-symbols--edit-outline-rounded] size-5"></span><span
				class="hidden 2xl:block">Edit</span
			>
		</button>
		<div
			class="dropdown join-item relative inline-flex grow [--auto-close:inside] [--placement:top]"
			bind:this={actionButtonShareMenu}
			{@attach initDropdown}
		>
			<button
				id="action-share"
				class="dropdown-toggle btn btn-secondary-container text-secondary-container-content w-full rounded-none"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="Share with"
			>
				<span class="icon-[tabler--share-2] size-5"></span><span class="hidden 2xl:block"
					>Share</span
				>
				<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-4"></span>
			</button>
			<ul
				class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden min-w-[15rem] shadow-xs"
				role="menu"
				aria-orientation="vertical"
				aria-labelledby="action-share"
			>
				{#each shareOptions as shareOption, i (i)}
					<ShareItem
						{resourceId}
						{shareOption}
						share={socketioPresentations?.shareEntity.bind(socketioPresentations)}
						closeShareMenu={() => window.HSDropdown.close(actionButtonShareMenu)}
					/>
				{/each}
				<!-- <li class="dropdown-footer gap-2">
								<button
									class="btn dropdown-item btn-text text-secondary content-center justify-start"
									>... more options</button
								>
							</li> -->
			</ul>
		</div>
		<button
			class="btn btn-error-container bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content join-item grow border-0"
			aria-label="Delete Button"
			name="id"
			onclick={() => !resourceId || socketioPresentations?.deleteEntity(resourceId)}
		>
			<span class="icon-[tabler--trash] size-5"></span><span class="hidden 2xl:block">Delete</span>
		</button>
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
										id: presentation.path.substring(1) || presentation.id
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
							<td>{presentation.path || presentation.id}</td>
							<td>{presentation.source}</td>
							<td>[Access]</td>
							<td>[Number]</td>
							<td>[Number]</td>
							<td>[Number]</td>
							<td>[Mb / Gb]</td>
							<td>{@render actionButtons(presentation.id)}</td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</Card>
