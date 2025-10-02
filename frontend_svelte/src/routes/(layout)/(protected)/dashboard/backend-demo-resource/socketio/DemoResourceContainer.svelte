<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { AccessShareOption, DemoResourceExtended, Identity } from '$lib/types';
	import { fade } from 'svelte/transition';
	import { Action } from '$lib/accessHandler';
	import ShareItem from '../../../../playground/components/ShareItem.svelte';
	import { AccessHandler } from '$lib/accessHandler';
	import IdBadge from '../../IdBadge.svelte';
	import type { HSDropdown, IHTMLElementFloatingUI } from 'flyonui/flyonui';
	import { SocketIO } from '$lib/socketio';

	let {
		demoResource = $bindable(),
		identities,
		edit = $bindable(false),
		// deleteResource = (_id: string) => {},
		// submitResource = (_resource: DemoResourceExtended) => {},
		// shareResource = (_accessPolicy: AccessPolicy) => {},
		socketio
	}: {
		demoResource: DemoResourceExtended;
		identities?: Identity[];
		edit?: boolean;
		// deleteResource?: (id: string) => void;
		// submitResource?: (resource: DemoResourceExtended) => void;
		// shareResource?: (accessPolicy: AccessPolicy) => void;
		socketio?: SocketIO;
	} = $props();

	// let editableDemoResource: DemoResourceExtended = $derived({ ...demoResource });

	let shareMenuElement: HTMLElement | undefined = $state(undefined);
	let shareMenu: HSDropdown | undefined = $derived(undefined);

	const initDropdown: Attachment = (_node: Element) => {
		import('flyonui/flyonui')
			.then(({ HSDropdown }) => {
				shareMenu = new HSDropdown(shareMenuElement as unknown as IHTMLElementFloatingUI);
				HSDropdown.autoInit();
			})
			.catch((error) => {
				console.error('Error loading HSDropdown:', error);
			});
	};
	const closeShareMenu = () => {
		if (shareMenu) {
			shareMenu.close();
		}
	};

	let formatedDate = $derived(
		demoResource.creation_date
			? new Date(demoResource.creation_date).toLocaleString('da-DK', { timeZone: 'CET' })
			: new Date(Date.now()).toLocaleString('da-DK', { timeZone: 'CET' })
	);
	if (demoResource.id?.slice(0, 4) === 'new_') edit = true;

	// TBD: reconsider the processing of identities - currently done both here and in the +page.svelte file.
	// get most of the work done in the +page.svelte file to avoid passing unnecessary data to component!
	// Adopt the simplifiaction of microsoftTeams into Identies and merge with other identity types from REST-API and move to +page.svelte
	// use the generation of shareOptions from REST-API and move to accessHandler.ts -> feed with identities and accessPolicies
	let shareOptions: AccessShareOption[] | undefined = $derived(
		AccessHandler.createShareOptions(identities, demoResource.access_policies)
	);
</script>

<div
	class="bg-base-300 shadow-shadow m-2 flex h-fit flex-col rounded-xl p-2 shadow-xl"
	transition:fade
>
	<div class="flex flex-row justify-between">
		{#if edit}
			<div class="input-filled input-base-content w-fit grow">
				<input
					type="text"
					placeholder="Name the demo resource"
					id="name_{demoResource.id}"
					class="input input-sm md:input-md"
					name="name"
					onblur={() => socketio?.submitEntity(demoResource)}
					bind:value={demoResource.name}
				/>
				<label class="input-filled-label" for="name_{demoResource.id}">Name</label>
			</div>
		{:else}
			<h5 class="title-small md:title-small lg:title base-content card-title">
				{demoResource.name}
			</h5>
		{/if}

		<!-- <h5
			contenteditable={edit}
			class="title justify-self-start"
			onblur={(event) => {
				// TBD: onblur changes edit to false, as DemoResourceContainer is getting reloaded
				demoResource.name = (event.target as HTMLElement)?.innerText || '';
				submitResource(demoResource);
			}}
		>
			{demoResource.name}
		</h5> -->
		<div class="label justify-self-end">
			{formatedDate}
		</div>
	</div>
	<div class="flex h-fit flex-row">
		<div class="body-small grow">
			{#if edit}
				<div class="textarea-filled textarea-base-content w-full">
					<textarea
						class="textarea h-fit"
						placeholder="Describe the demo resource here."
						id="description_{demoResource.id}"
						onblur={() => socketio?.submitEntity(demoResource)}
						name="description"
						bind:value={demoResource.description}
					>
					</textarea>
					<label class="textarea-filled-label" for="description_{demoResource.id}">
						Description
					</label>
				</div>
			{:else}
				<p class="body-small md:body text-primary-container-content">
					{demoResource.description || 'No description available'}
				</p>
			{/if}
			<!-- <p
				contenteditable={edit}
				onblur={(event) => {
					demoResource.description = (event.target as HTMLElement)?.innerText || '';
					submitResource(demoResource);
				}}
			>
				{demoResource.description}
			</p> -->
			<div class="flex flex-row gap-2">
				<IdBadge id={demoResource.id} />
				<div class="badge badge-xs badge-accent label-small shadow-outline shadow">
					{demoResource.access_right}
				</div>
			</div>
		</div>
		{#if demoResource.access_right === Action.WRITE || demoResource.access_right === Action.OWN}
			<div class="join flex flex-row items-end justify-center">
				<button
					class="btn btn-secondary-container text-secondary-container-content btn-sm join-item shadow-outline grow shadow-inner shadow-sm"
					aria-label="Edit Button"
					onclick={() => (edit = !edit)}
				>
					<span class="icon-[material-symbols--edit-outline-rounded] {!edit || 'hidden'}"></span>
					<span class="grid place-items-center {edit || 'hidden'}">
						<span
							class="icon-[material-symbols--edit-outline-rounded] col-start-1 row-start-1 size-3"
						></span>
						<span class="icon-[ic--outline-do-not-disturb] col-start-1 row-start-1 size-4"></span>
					</span>
				</button>
				{#if demoResource.access_right === Action.OWN}
					<div
						{@attach initDropdown}
						bind:this={shareMenuElement}
						class="dropdown join-item relative inline-flex grow [--placement:top]"
					>
						<!-- bind:this={actionButtonShareMenuElement} -->
						<button
							id="share-{demoResource.id}"
							class="dropdown-toggle btn btn-secondary-container text-secondary-container-content btn-sm shadow-outline w-full rounded-none shadow-sm"
							aria-haspopup="menu"
							aria-expanded="false"
							aria-label="Share with"
						>
							<span class="icon-[tabler--share-2]"></span>
							<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-4"></span>
						</button>
						<!-- {#if shareOptions}
							{#each shareOptions as shareOption (shareOption.identity_id)}
								{@attach initDropdown}
								<ShareItem
									resourceId={demoResource.id as string}
									{shareOption}
									share={socketio?.shareEntity.bind(socketio)}
								/>
							{/each}
						{/if} -->
						<ul
							class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden min-w-[15rem] shadow-xs"
							role="menu"
							aria-orientation="vertical"
							aria-labelledby="share-{demoResource.id}"
						>
							{#if shareOptions}
								{#each shareOptions as shareOption (shareOption.identity_id)}
									<ShareItem
										{@attach initDropdown}
										resourceId={demoResource.id as string}
										{shareOption}
										share={socketio?.shareEntity.bind(socketio)}
										{closeShareMenu}
									/>
								{/each}
							{/if}
							<li class="dropdown-footer gap-2">
								<button
									class="btn dropdown-item btn-text text-secondary content-center justify-start"
									>... more options</button
								>
							</li>
						</ul>
					</div>
					<button
						class="btn btn-error-container bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content btn-sm join-item shadow-outline grow border-0 shadow-sm"
						aria-label="Delete Button"
						name="id"
						onclick={() => !demoResource.id || socketio?.deleteEntity(demoResource.id)}
					>
						<span class="icon-[tabler--trash]"></span>
					</button>
				{/if}
			</div>
		{/if}
	</div>
</div>
