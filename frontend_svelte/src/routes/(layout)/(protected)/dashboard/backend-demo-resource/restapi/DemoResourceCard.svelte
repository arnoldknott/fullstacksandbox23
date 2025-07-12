<script lang="ts">
	import Card from '$components/Card.svelte';
	import { type SubmitFunction } from '@sveltejs/kit';
	import type { DemoResourceExtended, AccessPolicy, AccessShareOption, Identity } from '$lib/types';
	import { enhance } from '$app/forms';
	import { Action, AccessHandler } from '$lib/accessHandler';
	import type { IHTMLElementFloatingUI, HSDropdown } from 'flyonui/flyonui';
	// TBD: move to components folder
	import ShareItem from '../../../../playground/components/ShareItem.svelte';
	import type { ActionResult } from '@sveltejs/kit';

	let {
		demoResource,
		identities
	}: { demoResource: DemoResourceExtended; identities?: Identity[] } = $props();
	let id = $state(demoResource.id || 'new_' + Math.random().toString(36).substring(2, 9));
	let accessRight = $state(demoResource.access_right);
	let name = $state(demoResource.name || undefined);
	let description = $state(demoResource.description || undefined);
	let language = $state(demoResource.language || undefined);
	let category = $state(demoResource.category);
	let categoryId = $state(demoResource.category_id || undefined);
	let tags = $state(demoResource.tags || []);
	let creationDate = $state<Date | undefined>(demoResource.creation_date);
	let formattedCreationDate = $derived(creationDate?.toLocaleString('da-DK', { timeZone: 'CET' }));
	let accessPolicies = $state<AccessPolicy[] | undefined>(demoResource.access_policies);

	let edit = $state(demoResource.id?.slice(0, 4) === 'new_' ? true : false);

	// TBD. move to accessHandler.ts
	let shareOptions = $derived(AccessHandler.createShareOptions(identities, accessPolicies));

	let flag = $state(
		language === 'en-US'
			? 'united-states'
			: language === 'da-DK'
				? 'denmark'
				: language === 'de-DE'
					? 'germany'
					: false
	);

	let card: Card;
	let createUpdateForm = $state<HTMLFormElement | null>(null);

	let dropdownMenuElement = $state<HTMLElement | null>(null);
	let dropdownShareDropdownElement = $state<HTMLElement | null>(null);
	let dropdownMenu = $state<HSDropdown | null>(null);
	let dropdownShareDropdown = $state<HSDropdown | null>(null);

	const loadHSDropdown = async () => {
		const { HSDropdown } = await import('flyonui/flyonui');
		return HSDropdown;
	};

	$effect(() => {
		loadHSDropdown().then((LoadedHSDropdown) => {
			dropdownMenu = new LoadedHSDropdown(dropdownMenuElement as unknown as IHTMLElementFloatingUI);
			dropdownShareDropdown = new LoadedHSDropdown(
				dropdownShareDropdownElement as unknown as IHTMLElementFloatingUI
			);
		});
	});

	let minWidthMenu = $derived.by(() =>
		dropdownMenuElement
			? window.innerWidth - dropdownMenuElement.getBoundingClientRect().right < 70
				? 'min-w-60'
				: ''
			: ''
	);

	const formAction = $derived(id.slice(0, 4) === 'new_' ? '?/post' : '?/put');

	const triggerSubmit = async () => {
		createUpdateForm?.requestSubmit();
	};

	const createOrUpdateResource: SubmitFunction = async ({ formData }) => {
		if (id.slice(0, 4) !== 'new_') {
			formData.append('id', id);
		}
		// TBD: add validation here - if not all required fields are filled, otherwise cancel
		// and mark the missing fields invalid
		return async ({ result }) => {
			if (result.type === 'success') {
				if (id.slice(0, 4) === 'new_') {
					id = result.data?.id;
					creationDate = result.data?.creationDate;
				}
			}
		};
	};

	// TBD: refactor into reusing the automatic rerun of the load function to update the page data.
	const handleRightsChangeResponse = async (result: ActionResult, update: () => void) => {
		if (result.type === 'success') {
			if (!result.data?.confirmedNewAction) {
				// remove access policy
				accessPolicies = accessPolicies?.filter(
					(policy) => policy.identity_id !== result.data?.identityId
				);
			} else if (accessPolicies?.find((policy) => policy.identity_id === result.data?.identityId)) {
				// update existing access policy
				let existingPolicy = accessPolicies?.find(
					(policy) => policy.identity_id === result.data?.identityId
				);
				if (existingPolicy) {
					existingPolicy.action = result.data?.confirmedNewAction;
					existingPolicy.public = result.data?.public || existingPolicy.public;
				}
			} else if (result.data?.confirmedNewAction) {
				// add new access policy
				accessPolicies?.push({
					identity_id: result.data?.identityId,
					resource_id: id,
					action: result.data?.confirmedNewAction,
					public: result.data?.public
				});
			} else {
				// TBD: handle error - show error message
				console.error('Error handling rights change response:', result);
			}
		} else if (result.type === 'error') {
			console.error(
				'🔥 Error handling rights change response (server returned type error):',
				result
			);
			// handle error: show error message
		}
		update();
	};
</script>

{#snippet header()}
	<div class="flex justify-between">
		<div>
			{#if edit}
				<div class="input-filled input-base-content w-fit grow">
					<input
						type="text"
						placeholder="Name the demo resource"
						class="input input-sm md:input-md"
						id="name_{id}"
						form="form_{id}"
						name="name"
						onblur={() => triggerSubmit()}
						bind:value={name}
					/>
					<label class="input-filled-label" for="name_{id}">Name</label>
				</div>
			{:else}
				<h5 class="title-small md:title lg:title-large base-content card-title">
					{name}
				</h5>
				<p class="label-small md:label text-secondary">
					{formattedCreationDate}
					<!-- {creationDate?.toLocaleString('da-DK', { timeZone: 'CET' }) } -->
				</p>
			{/if}
		</div>
		<div class="flex flex-row items-start gap-4">
			{#if category}
				<span
					id={categoryId}
					class="label-small md:label lg:label-large badge badge-secondary shadow-secondary shadow-xs"
				>
					{category}
				</span>
			{/if}
			{#if flag}
				<span class="icon-[twemoji--flag-{flag}] size-6"></span>
			{/if}
			{#if accessRight === Action.WRITE || accessRight === Action.OWN}
				<div
					class="dropdown relative inline-flex rtl:[--placement:bottom-end]"
					bind:this={dropdownMenuElement}
				>
					<span
						id="dropdown-menu-icon-{id}"
						class="dropdown-toggle icon-[tabler--dots-vertical] size-6"
						role="button"
						aria-haspopup="menu"
						aria-expanded="false"
						aria-label="Dropdown"
					></span>
					<ul
						class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden {minWidthMenu} shadow-xs"
						role="menu"
						aria-orientation="vertical"
						aria-labelledby="dropdown-menu-icon-{id}"
					>
						<li class="items-center">
							<button
								class="btn dropdown-item btn-text text-base-content content-center justify-start"
								aria-label="Edit Button"
								onclick={() => (edit ? (edit = false) : (edit = true))}
							>
								<span class="icon-[material-symbols--edit-outline-rounded]"></span>
								Edit
							</button>
						</li>
						{#if accessRight === Action.OWN}
							<li
								class="dropdown relative items-center [--offset:15] [--placement:right-start] max-sm:[--placement:bottom-start]"
								bind:this={dropdownShareDropdownElement}
							>
								<button
									id="share-{id}"
									class="dropdown-toggle btn dropdown-item btn-text text-base-content content-center justify-start"
									aria-haspopup="menu"
									aria-expanded="false"
									aria-label="Share with"
								>
									<span class="icon-[tabler--share-2]"></span>
									Share
									<span
										class="icon-[tabler--chevron-right] dropdown-open:rotate-180 size-4 rtl:rotate-180"
									></span>
								</button>
								<ul
									class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 shadow-xs hidden min-w-60"
									role="menu"
									aria-orientation="vertical"
									aria-labelledby="share-{id}"
								>
									{#if shareOptions}
										<form
											method="POST"
											name="shareForm-resource-{id}"
											use:enhance={async () => {
												dropdownShareDropdown?.close();
												dropdownMenu?.close();
												return async ({ result, update }) => {
													handleRightsChangeResponse(result, update);
												};
											}}
										>
											{#each shareOptions as shareOption (shareOption.identity_id)}
												<ShareItem resourceId={id} {shareOption} />
											{/each}
											<li class="dropdown-footer gap-2">
												<button
													class="btn dropdown-item btn-text text-base-content content-center justify-start"
													>... more options</button
												>
											</li>
										</form>
									{/if}
								</ul>
							</li>
							<li class="dropdown-footer gap-2">
								<form method="POST" use:enhance={() => card.remove()}>
									<button
										class="btn dropdown-item btn-error btn-text content-center justify-start"
										aria-label="Delete Button"
										name="id"
										value={id}
										formaction="?/delete"><span class="icon-[tabler--trash]"></span>Delete</button
									>
								</form>
							</li>
						{/if}
					</ul>
				</div>
			{/if}
		</div>
	</div>
{/snippet}

<Card bind:this={card} {id} {header} {footer}>
	{#if edit}
		<form
			method="POST"
			use:enhance={createOrUpdateResource}
			bind:this={createUpdateForm}
			id="form_{id}"
			action={formAction}
		>
			<div class="textarea-filled textarea-base-content w-full">
				<textarea
					class="textarea"
					placeholder="Describe the demo resource here."
					id="description_{id}"
					onblur={() => triggerSubmit()}
					name="description"
					bind:value={description}
				>
				</textarea>
				<label class="textarea-filled-label" for="description_{id}"> Description </label>
			</div>
		</form>
	{:else}
		<p class="body-small md:body text-primary-container-content">
			{description || 'No description available'}
		</p>
	{/if}
</Card>

{#snippet footer()}
	<div class="card-actions flex justify-end">
		<div>
			{#each tags as tag (tag)}
				<span
					class="label-small md:label lg:label-large badge badge-neutral shadow-neutral shadow-xs"
					>{tag}</span
				>
			{/each}
		</div>
		{#if edit}
			<button
				class="btn-success-container btn btn-gradient rounded-full"
				onclick={() => (edit = false)}
				aria-label="Done"
			>
				<span class="icon-[mingcute--check-2-fill]"></span> Done
			</button>
			<form
				method="POST"
				use:enhance={({ cancel }) => {
					if (id.slice(0, 4) === 'new_') cancel();
					card.remove();
				}}
			>
				<button
					class="btn-error-container btn btn-gradient rounded-full"
					value={id}
					formaction="?/delete"
					aria-label="Done"
				>
					<span class="icon-[mingcute--check-2-fill]"></span> Delete
				</button>
			</form>
		{/if}
	</div>
{/snippet}
