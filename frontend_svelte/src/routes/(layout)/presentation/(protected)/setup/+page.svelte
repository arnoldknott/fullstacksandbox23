<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import { fade, slide } from 'svelte/transition';

	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import Display from '$components/Display.svelte';
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, PresentationExtended } from '$lib/types';

	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import ShareItem from '../../../playground/components/ShareItem.svelte';
	import type { PageData } from './$types';
	import ActionButtons from './ActionButtons.svelte';
	import FormElement from './FormElement.svelte';

	let { data }: { data: PageData } = $props();

	// uses the one, that gets set in sidebar and communicated
	// through the search params of the url
	let debug = $derived(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		debug = page.url.searchParams.get('debug') === 'true';
	});

	let socketioPresentations: SocketIO<PresentationExtended> = $state()!;
	onMount(() => {
		socketioPresentations = new SocketIO(
			{
				namespace: '/presentation',
				sessionId: data?.session?.sessionId || '',
				queryParams: {
					'request-access-data': true,
					'identity-ids': data.payload.identities.map((identity) => identity.id).join(',')
				}
			},
			{
				template: {
					source: 'intern:',
					path: '',
					access_right: Action.OWN
					// creation_date: new Date(Date.now()) // TBD: Check if this is necessary?
				}
			}
		);

		socketioPresentations.identities = data.payload.identities;
		socketioPresentations.addSelection('selected');
	});

	$effect(() => {
		socketioPresentations.entities = data.payload.presentations || [];
	});

	onDestroy(() => {
		socketioPresentations?.client.disconnect();
	});

	let hideNewPresentationCard: boolean = $state(!(page.url.searchParams.get('new') === 'true'));

	const submitPresentation = () => {
		const newPath = socketioPresentations.pendingEntities[0].path?.trim() ?? '';
		socketioPresentations.pendingEntities[0].path =
			newPath && !newPath.startsWith('/') ? `/${newPath}` : newPath;
		socketioPresentations.submitEntity();
		hideNewPresentationCard = true;
	};

	// TBD: move this calculation to EntityContainer (or AccessHandler) class!
	let shareOptionsForNewPresentation: AccessShareOption[] = $derived(
		AccessHandler.createShareOptions(
			socketioPresentations.identities,
			socketioPresentations.accessPolicies[socketioPresentations.pendingEntities[0].id]
		) || []
	);

	// For showing existing presentations:
	let viewMode = $state<'preview' | 'grid' | 'list'>('list');

	// Selectors:
	let selectAllPresentations = $state(false);
</script>

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

{#snippet newPresentationFooter()}
	<div class="ml-5 flex flex-row justify-end gap-4">
		<button
			class="btn btn-secondary-container btn-gradient shadow-outline rounded-full shadow"
			aria-label="Cancel"
			onclick={() => {
				hideNewPresentationCard = true;
			}}><span class="icon-[tabler--x] size-5"></span>Cancel</button
		>
		<button
			class="btn btn-primary-container btn-gradient shadow-outline rounded-full shadow"
			aria-label="Save new presentation"
			onclick={() => submitPresentation()}
			><span class="icon-[tabler--send-2] size-5"></span>Save</button
		>
	</div>
{/snippet}

{#snippet warning()}
	<span class="icon-[fluent-color--warning-24] size-4"></span>
{/snippet}

<!-- <JsonData data={data.payload.identities} /> -->

{#if socketioPresentations?.pendingEntities[0]}
	<Card
		id={socketioPresentations.pendingEntities[0].id}
		title="New presentation"
		footer={newPresentationFooter}
		closeButton
		bind:hidden={hideNewPresentationCard}
	>
		<div class="flex w-full flex-wrap gap-6">
			<div class="grow">
				<FormElement title="Slug" description={slugDescription} extraClasses="w-full">
					<div class="md:flex-cols-2 wrap flex gap-2">
						<code class="mt-5 shrink">{page.url.origin}/presentation/</code>
						<div class="input-filled input-primary w-full">
							<input
								type="text"
								placeholder=""
								class="input"
								id="slugInput"
								bind:value={socketioPresentations.pendingEntities[0].path}
							/>
							<label class="input-filled-label" for="slugInput"
								>[add the path to your presentation here]</label
							>
						</div>
					</div>
				</FormElement>
				<FormElement title="Source" description={sourceDescription} extraClasses="max-w-300">
					{@render warning()} For now, all presentations are <IdBadge id="intern" />, e.g. hosted
					with the source code of this platform. ON the long run, <IdBadge id="Github" />, <IdBadge
						id="Gitlab"
					/>, <IdBadge id="OneDrive" />, <IdBadge id="GoogleDrive" /> and other sources should be supported
					as well.
				</FormElement>
				<FormElement title="Questions" extraClasses="max-w-300">
					{@render warning()} Link interactive questions to your presentation, so they can be answered
					while going through the presentation. Linking exisiting questions, also links their answers,
					copying existing questions creates a new question without any answers.
				</FormElement>
				<FormElement title="Links" extraClasses="max-w-300">
					{@render warning()} Maybe there's a need to add related links and / or embeddings. The service
					to the user could be to check the aliveness of the links - if a link returns a 404, the user
					gets a notification.
				</FormElement>
				<FormElement title="Files" extraClasses="max-w-300">
					{@render warning()}Select existing files or drop new files into a container to upload and
					make available to the presentation. This is the place to store binaries, so they can be
					accessed via the presentation api and used in the presentation.
				</FormElement>
			</div>

			<FormElement title="Access" description={accessDescription} extraClasses="max-w-100">
				<ul class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg p-2 shadow-inner">
					{#each shareOptionsForNewPresentation, i (i)}
						<ShareItem
							resourceId={socketioPresentations.pendingEntities[0].id}
							// No need to bind, as it is anyways handled through the entityContainer's methods and the socketio's submitEntity method.
							shareOption={shareOptionsForNewPresentation[i]}
							socketio={socketioPresentations}
							// share={socketioPresentations?.shareEntity.bind(socketioPresentations)}
							wide
						/>
					{/each}
				</ul>
			</FormElement>
		</div>
	</Card>
{:else if !socketioPresentations?.pendingEntities[0] && !hideNewPresentationCard}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
	</div>
{/if}

{#snippet existingPresentationsHeader()}
	<div class="flex justify-between">
		<Title id="existingPresentations" class="grow">Overview</Title>
		<div class="flex flex-row items-center justify-center">
			{#if hideNewPresentationCard || !socketioPresentations?.pendingEntities[0]}
				<button
					transition:fade={{ duration: 600 }}
					class="btn btn-primary-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
					aria-label="Add new presentation"
					onclick={() => (hideNewPresentationCard = false)}
				>
					<!-- onclick={() => goto(resolve('/(layout)/presentation/(protected)/setup/new'))} -->
					<span class="icon-[fa6-solid--plus] size-5"></span>
					<!-- <span class="hidden ">Add</span> -->
					<span class="hidden sm:inline">Add new</span>
					<span class="hidden md:inline">presentation</span>
				</button>
			{/if}
			<div class="join shadow-outline rounded-full shadow-sm">
				<button
					aria-label="Preview"
					class="btn join-item btn-secondary btn-gradient btn-sm rounded-l-full py-4 {viewMode !==
					'preview'
						? 'opacity-60'
						: ''}"
					onclick={() => (viewMode = 'preview')}
				>
					<span class="icon-[material-symbols-light--preview-outline] size-5"></span>
				</button>
				<button
					aria-label="Grid"
					class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline py-4 shadow {viewMode !==
					'grid'
						? 'opacity-60'
						: ''}"
					onclick={() => (viewMode = 'grid')}
				>
					<span class="icon-[gridicons--grid] size-5"></span>
				</button>
				<button
					aria-label="List"
					class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline rounded-r-full py-4 shadow {viewMode !==
					'list'
						? 'opacity-60'
						: ''}"
					onclick={() => (viewMode = 'list')}
				>
					<span class="icon-[material-symbols-light--table-outline] size-5"></span>
				</button>
			</div>
		</div>
	</div>
{/snippet}

<Card id="existing-presentations" header={existingPresentationsHeader} extraClasses="mt-6">
	<div class="w-full overflow-x-auto {viewMode !== 'preview' ? 'hidden' : ''}">
		<p class="bg-warning text-warning-content rounded-lg p-4">Preview mode is not developed yet</p>
	</div>
	<div class="w-full overflow-x-auto {viewMode !== 'grid' ? 'hidden' : ''}">
		<p class="bg-warning text-warning-content rounded-lg p-4">
			Grid view mode is not developed yet
		</p>
	</div>
	<div class="w-full {viewMode !== 'list' ? 'hidden' : ''}">
		<div class="overflow-x-auto">
			<table class="table w-full overflow-hidden rounded-2xl">
				<thead>
					<tr
						class="shadow-base-shadow bg-base-300 inset-ring-outline-variant rounded-t-2xl shadow inset-ring *:first:rounded-tl-2xl *:last:rounded-tr-2xl"
					>
						<th>
							<input
								id="select-all-presentations"
								type="checkbox"
								class="checkbox checkbox-sm checkbox-secondary"
								bind:checked={selectAllPresentations}
								// onchange={() => (selectAllPresentations = !selectAllPresentations)}
								onchange={(event) => {
									if ((event.target as HTMLInputElement).checked) {
										selectAllPresentations = true;
										socketioPresentations?.entities?.forEach((presentation) => {
											socketioPresentations?.selections['selected']?.push(presentation.id);
										});
									} else {
										selectAllPresentations = false;
										socketioPresentations?.selections['selected']?.splice(0);
									}
								}}
							/>
						</th>
						<th class="title text-base-content w-3/5 font-medium normal-case">Id / Slug</th>
						<th class="title text-base-content text-center font-medium normal-case">Source</th>
						<th class="title text-base-content text-center font-medium normal-case">Access</th>
						<th class="title text-base-content text-center font-medium normal-case"
							># <span class="icon-[codicon--question] size-4"></span></th
						>
						<th class="title text-base-content text-center font-medium normal-case"
							># <span class="icon-[line-md--link] size-4"></span></th
						>
						<th class="title text-base-content text-center font-medium normal-case"
							># <span class="icon-[tabler--file] size-4"></span></th
						>
						<th class="title text-base-content text-center font-medium normal-case"
							><span class="icon-[fluent-mdl2--offline-storage] size-4 text-center"></span></th
						>
						<th
							class="title text-base-content w-px text-center font-medium whitespace-nowrap normal-case"
							>Actions</th
						>
					</tr>
				</thead>
				<tbody class="bg-base-150 shadow-base-shadow rounded-b-2xl shadow shadow-inner">
					{#if (socketioPresentations?.entities?.length ?? 0) === 0}
						<tr>
							<td colspan={9} class="text-center">
								No presentations yet. Create one by sending a POST request to the /presentation
								endpoint.
							</td>
						</tr>
					{:else}
						{#if socketioPresentations?.selections['selected']?.length > 1}
							<tr
								transition:slide={{ duration: 300 }}
								class="bg-base-300 inset-ring-outline-variant inset-ring"
							>
								<th></th>
								<th colspan={8}>
									add sort, search, filter, actions for multiple selected presentations</th
								>
							</tr>
						{/if}
						{#each socketioPresentations.entities as presentation (presentation.id)}
							<tr
								animate:flip={{ duration: 300 }}
								transition:slide={{ duration: 300 }}
								class="hover:bg-base-250 last:hover:rounded-b-2xl"
							>
								<!-- <td>
								<a
									href={resolve('/(layout)/presentation/(protected)/setup/[id]', {
										id: presentation?.path?.substring(1) || presentation.id
									})}
									aria-label={`Setup presentation ${presentation.path || presentation.id}`}
								>
									<button
										type="button"
										class="btn btn-info-container btn-gradient shadow-outline btn-circle shadow-sm"
										aria-label={`Setup presentation ${presentation.path || presentation.id}`}
									>
										<span class="icon-[mingcute--arrow-right-fill] size-4"></span>
									</button>
								</a>
							</td> -->
								<td>
									<input
										id="select-all-presentations"
										type="checkbox"
										class="checkbox checkbox-sm checkbox-secondary"
										onchange={(event) => {
											if ((event.target as HTMLInputElement).checked) {
												socketioPresentations?.addToSelection('selected', [presentation.id]);
											} else {
												selectAllPresentations = false;
												socketioPresentations?.removeFromSelection('selected', [presentation.id]);
											}
										}}
										checked={socketioPresentations?.selections['selected']?.includes(
											presentation.id
										) ?? false}
										// bind:checked={addThisOneToSelection(presentation.id) - not a bind, but an onChange?}
									/>
								</td>
								<td class="max-w-0">
									<IdBadge id={presentation.id} />
									<a
										href={resolve('/(layout)/presentation/[slug]', {
											slug: presentation?.path?.substring(1) || presentation.id
										})}
										aria-label={`Setup presentation ${presentation.path || presentation.id}`}
										class="link link-primary link-animated block truncate"
									>
										{presentation.path || presentation.id}
									</a>
								</td>
								<td class="text-center"><IdBadge id="intern" /></td>
								<!-- <td>{presentation.source}</td> -->
								<td class="text-center">[Access]</td>
								<td class="text-center">{presentation.questions?.length ?? 0}</td>
								<td class="text-center">[Num]</td>
								<td class="text-center">[Num]</td>
								<td class="text-center">[Size]</td>
								<td class="w-px py-1 text-center align-middle whitespace-nowrap">
									<ActionButtons
										resourceId={presentation.id}
										accessRight={socketioPresentations?.accessRights[presentation.id]}
										socketio={socketioPresentations}
									/>
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
	</div>
</Card>

{#if debug}
	<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
		<div>
			<Title id="pendingEntities">Pending Entities</Title>
			<JsonData data={socketioPresentations?.pendingEntities ?? []} />
			<Title id="entities">Entities</Title>
			<JsonData data={socketioPresentations?.entities ?? []} />
		</div>
		<div>
			<Title id="identities">Selected</Title>
			<JsonData data={socketioPresentations?.selections['selected'] ?? []} />
			<Title id="identities">Identities</Title>
			<JsonData data={socketioPresentations?.identities ?? []} />
		</div>
		<div>
			<Title id="accessRights">Access Rights</Title>
			<JsonData data={socketioPresentations?.accessRights ?? []} />
			<Title id="accessPolicies">Access Policies</Title>
			<JsonData data={socketioPresentations?.accessPolicies ?? []} />
		</div>
	</div>
{/if}
