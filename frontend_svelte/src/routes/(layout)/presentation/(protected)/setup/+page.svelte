<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { slide } from 'svelte/transition';

	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import Display from '$components/Display.svelte';
	import Title from '$components/Title.svelte';
	// import JsonData from '$components/JsonData.svelte';
	import { AccessHandler, Action, IdentityType } from '$lib/accessHandler';
	import { SocketIO, type SocketioStatus } from '$lib/socketio.svelte';
	import type { AccessShareOption, PresentationExtended } from '$lib/types';
	import { initDropdown } from '$lib/userInterface';

	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import ShareItem from '../../../playground/components/ShareItem.svelte';
	import type { PageData } from './$types';
	import FormElement from './FormElement.svelte';

	let { data }: { data: PageData } = $props();

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

		socketioPresentations.client.on('status', (data: SocketioStatus) => {
			if ('success' in data && data.success === 'created') {
				const publicShare = shareOptions.filter(
					(shareOption) => shareOption.identity_type === IdentityType.PUBLIC
				);
				if (publicShare[0].action) {
					socketioPresentations?.shareEntity({
						resource_id: data.id,
						action: publicShare[0].action,
						public: true
					});
				}
			}
		});
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

	const shareOptions: AccessShareOption[] = $state([
		{
			identity_id: undefined,
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

<Display id="overview-presentations">Presentations</Display>

{#snippet newPresentationHeader()}
	<Title id="newPresentation">New presentation</Title>
{/snippet}

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
			class="btn btn-secondary btn-gradient shadow-outline rounded-lg shadow"
			aria-label="Cancel"
			onclick={() => {
				hideNewPresentationCard = true;
			}}><span class="icon-[tabler--x] size-5"></span>Cancel</button
		>
		<button
			class="btn btn-primary btn-gradient shadow-outline rounded-lg shadow"
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

<!-- TBD: consider making the showCard a bindable prop in component Card and use it for example for the close button -->
{#if socketioPresentations?.pendingEntities[0]}
	<!-- <div transition:fade={{ duration: 600 }}> -->
	<Card
		id={socketioPresentations.pendingEntities[0].id}
		header={newPresentationHeader}
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

			<FormElement title="Access" description={accessDescription} extraClasses="max-w-96">
				{@render warning()} Only the public access gets currently submitted with the presentation!
				<ul
					class="bg-base-150 shadow-outline max-h-48 max-w-fit overflow-y-auto rounded-lg p-2 shadow-inner"
				>
					{#each shareOptions, i}
						<ShareItem
							resourceId={socketioPresentations.pendingEntities[0].id}
							bind:shareOption={shareOptions[i]}
							share={socketioPresentations?.shareEntity.bind(socketioPresentations)}
							wide
						/>
					{/each}
				</ul>
			</FormElement>
		</div>
	</Card>
	<!-- </div> -->
{:else if !socketioPresentations?.pendingEntities[0] && !hideNewPresentationCard}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
	</div>
{/if}

{#snippet existingPresentationsHeader()}
	<div class="flex justify-between">
		<Title id="existingPresentations" class="grow">Overview</Title>
		<div class="flex flex-row items-center justify-center">
			<button
				class="btn btn-primary-container btn-gradient btn-sm shadow-outline mx-4 rounded-full shadow-sm"
				aria-label="Add new presentation"
				onclick={() => (hideNewPresentationCard = false)}
			>
				<!-- onclick={() => goto(resolve('/(layout)/presentation/(protected)/setup/new'))} -->
				<span class="icon-[fa6-solid--plus] size-4"></span>
				<!-- <span class="hidden ">Add</span> -->
				<span class="hidden sm:inline">Add new</span>
				<span class="hidden md:inline">presentation</span>
			</button>
			<div class="join rounded-lg">
				<button
					aria-label="Preview"
					class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline rounded- py-4 shadow {viewMode !==
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
					class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline py-4 shadow {viewMode !==
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

{#snippet actionButtons(resourceId: string)}
	<div class="join inline-flex flex-row">
		<!-- <a
			href={resolve('/(layout)/presentation/(protected)/setup/[id]', {
				id: path || resourceId
			})}
			aria-label={`Setup presentation ${path || resourceId}`}
			class=""
		> -->
		<button
			class="btn btn-secondary-container btn-gradient btn-sm text-secondary-container-content join-item shadow-outline shadow-sm"
			aria-label="Edit Button"
			onclick={() =>
				goto(resolve('/(layout)/presentation/(protected)/setup/[id]', { id: resourceId }))}
		>
			<span class="icon-[material-symbols--edit-outline-rounded] size-4"></span>
			<!-- <span
					class="hidden 2xl:block">Edit</span
				> -->
		</button>
		<!-- </a> -->
		<div
			class="dropdown join-item relative inline-flex [--auto-close:inside] [--placement:top]"
			bind:this={actionButtonShareMenu}
			{@attach initDropdown}
		>
			<button
				id="action-share"
				class="dropdown-toggle btn btn-secondary-container btn-gradient btn-sm text-secondary-container-content shadow-outline w-full rounded-none shadow-sm"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="Share with"
			>
				<span class="icon-[tabler--share-2] size-4"></span>
				<!-- <span class="hidden 2xl:block"
					>Share</span
				> -->
				<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-3"></span>
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
			class="btn btn-error-container btn-gradient btn-sm bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content join-item shadow-outline border-0 shadow-sm"
			aria-label="Delete Button"
			name="id"
			onclick={() => !resourceId || socketioPresentations?.deleteEntity(resourceId)}
		>
			<span class="icon-[tabler--trash] size-4"></span>
			<!-- <span class="hidden 2xl:block">Delete</span> -->
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
					<th class="title text-base-content w-3/5 font-medium normal-case">Slug / Id</th>
					<th class="title text-base-content font-medium normal-case">Source</th>
					<th class="title text-base-content font-medium normal-case">Access</th>
					<th class="title text-base-content font-medium normal-case"
						># <span class="icon-[codicon--question] size-4"></span></th
					>
					<th class="title text-base-content font-medium normal-case"
						># <span class="icon-[line-md--link] size-4"></span></th
					>
					<th class="title text-base-content font-medium normal-case"
						># <span class="icon-[tabler--file] size-4"></span></th
					>
					<th class="title text-base-content font-medium normal-case"
						><span class="icon-[fluent-mdl2--offline-storage] size-4"></span></th
					>
					<th class="title text-base-content w-px pr-0 font-medium whitespace-nowrap normal-case"
						>Actions</th
					>
				</tr>
			</thead>
			<tbody>
				{#if (socketioPresentations?.entities?.length ?? 0) === 0}
					<tr>
						<td colspan={8} class="text-center">
							No presentations yet. Create one by sending a POST request to the /presentation
							endpoint.
						</td>
					</tr>
				{:else}
					{#each socketioPresentations.entities as presentation (presentation.id)}
						<tr class="hover:bg-base-300">
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
							<td class="max-w-0">
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
							<td><IdBadge id="intern" /></td>
							<!-- <td>{presentation.source}</td> -->
							<td>[Access]</td>
							<td>[Num]</td>
							<td>[Num]</td>
							<td>[Num]</td>
							<td>[Size]</td>
							<td class="w-px px-0 py-1 text-right align-middle whitespace-nowrap"
								>{@render actionButtons(presentation.id)}</td
							>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</Card>
