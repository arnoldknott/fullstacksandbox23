<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { AccessPolicy, AccessShareOption, DemoResourceExtended, Identity } from '$lib/types';
	import { fade } from 'svelte/transition';
	import { Action } from '$lib/accessHandler';
	import ShareItem from '../../../../playground/components/ShareItem.svelte';
	import { AccessHandler } from '$lib/accessHandler';
	import IdBadge from '../../IdBadge.svelte';

	let {
		demoResource, // = $bindable(),
		identities,
		edit = $bindable(false),
		deleteResource = (_id: string) => {},
		submitResource = (_resource: DemoResourceExtended) => {},
		share = (_accessPolicy: AccessPolicy) => {}
	}: {
		demoResource: DemoResourceExtended;
		identities?: Identity[];
		edit?: boolean;
		deleteResource?: (id: string) => void;
		submitResource?: (resource: DemoResourceExtended) => void;
		share?: (accessPolicy: AccessPolicy) => void;
	} = $props();

	let editableDemoResource: DemoResourceExtended = $derived({ ...demoResource });

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

	const initDropdown: Attachment = (_node: Element) => {
		import('flyonui/flyonui')
			.then(({ HSDropdown }) => {
				HSDropdown.autoInit();
			})
			.catch((error) => {
				console.error('Error loading HSDropdown:', error);
			});
	};
</script>

<div class="bg-base-300 shadow-shadow m-2 flex flex-col rounded-xl p-2 shadow-xl" transition:fade>
	<div class="flex flex-row justify-between">
		<h5
			contenteditable={edit}
			class="title justify-self-start"
			onblur={(event) => {
				// TBD: onblur changes edit to false, as DemoResourceContainer is getting reloaded
				editableDemoResource.name = (event.target as HTMLElement)?.innerText || '';
				submitResource(editableDemoResource);
			}}
		>
			{editableDemoResource.name}
		</h5>
		<div class="label justify-self-end">
			{formatedDate}
		</div>
	</div>
	<div class="flex flex-row">
		<div class="body-small grow">
			<p
				contenteditable={edit}
				onblur={(event) => {
					editableDemoResource.description = (event.target as HTMLElement)?.innerText || '';
					submitResource(editableDemoResource);
				}}
			>
				{editableDemoResource.description}
			</p>
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
					class="btn btn-secondary-container text-secondary-container-content btn-sm join-item grow"
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
						class="dropdown join-item relative inline-flex grow [--placement:top]"
					>
						<!-- bind:this={actionButtonShareMenuElement} -->
						<button
							id="share-{demoResource.id}"
							class="dropdown-toggle btn btn-secondary-container text-secondary-container-content btn-sm w-full rounded-none"
							aria-haspopup="menu"
							aria-expanded="false"
							aria-label="Share with"
						>
							<span class="icon-[tabler--share-2]"></span>
							<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-4"></span>
						</button>

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
										{share}
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
						class="btn btn-error-container bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content btn-sm join-item grow border-0"
						aria-label="Delete Button"
						name="id"
						onclick={() => !demoResource.id || deleteResource(demoResource.id)}
					>
						<span class="icon-[tabler--trash]"></span>
					</button>
				{/if}
			</div>
		{/if}
	</div>
</div>
