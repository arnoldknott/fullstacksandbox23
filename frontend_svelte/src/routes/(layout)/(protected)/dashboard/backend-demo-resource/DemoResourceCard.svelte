<script lang="ts">
	import Card from '$components/Card.svelte';
	import { type SubmitFunction } from '@sveltejs/kit';
	import type { DemoResourceExtended, AccessPolicy } from '$lib/types';
	import { enhance } from '$app/forms';
	import type { MicrosoftTeamBasicExtended } from '$lib/types';
	// import { AccessHandler, Action } from '$lib/accessHandler';
	import { AccessHandler, type Action } from '$lib/accessHandler';
	import type { IHTMLElementFloatingUI, HSDropdown } from 'flyonui/flyonui';
	// import { on } from 'svelte/events';

	let {
		demoResource,
		microsoftTeams
	}: { demoResource?: DemoResourceExtended; microsoftTeams?: MicrosoftTeamBasicExtended[] } =
		$props();
	let id = $state(demoResource?.id || 'new_' + Math.random().toString(36).substring(2, 9));
	let userRight = $state(demoResource?.user_right || 'read');
	let name = $state(demoResource?.name || undefined);
	let description = $state(demoResource?.description || undefined);
	let language = $state(demoResource?.language || undefined);
	let category = $state(demoResource?.category);
	let categoryId = $state(demoResource?.category_id || undefined);
	let tags = $state(demoResource?.tags || []);
	let creationDate = $state<Date | undefined>(demoResource?.creation_date);
	let formattedCreationDate = $derived(creationDate?.toLocaleString('da-DK', { timeZone: 'CET' }));
	let accessPolicies = $state<AccessPolicy[] | undefined>(demoResource?.access_policies);

	let edit = $state(demoResource ? false : true);

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

	const formAction = $derived(id.slice(0, 4) === 'new_' ? '?/post' : '?/put');

	let teamRight = $state('read');
	// just for preventing linting errors:
	$effect(() => console.log(teamRight));

	// $effect(() => {
	// 	console.log('=== DemoResourceCard.svelte - teamRight ===');
	// 	console.log(teamRight);
	// });

	const accessAction = (identityId: string) =>  accessPolicies ? AccessHandler.getRights(identityId, accessPolicies) : null

	const iconMapping = (rights: Action | null) => {
		return rights === 'own'
			? 'icon-[tabler--key-filled] bg-success'
			: rights === 'write'
				? 'icon-[material-symbols--edit-outline-rounded] bg-warning'
				: rights === 'read'
					? 'icon-[tabler--eye] bg-neutral'
					: 'icon-[tabler--ban] bg-error';
	};

	// let identitiesRightsMap = $derived.by(() => {
	// 	let rightsMapping = new Map<string, Action | null>();
	// 	microsoftTeams?.forEach((team) => {
	// 		// TBD: turn into an object, that also hold information if right is assigned or not
	// 		rightsMapping.set(team.id, AccessHandler.getRights(team.id, team.access_policies));
	// 	});
	// 	return rightsMapping;
	// });

	// $effect(() => {
	// 	console.log('=== DemoResourceCard.svelte - identitiesRightsMap ===');
	// 	console.log(identitiesRightsMap);
	// });

	// console.log('=== DemoResourceCard.svelte - demoResource - accessPolicies ===');
	// console.log(demoResource?.access_policies);

	const triggerSubmit = async () => {
		createUpdateForm?.requestSubmit();
	};

	const createOrUpdateResource: SubmitFunction = async ({ formData }) => {
		// console.log('=== createOrUpdateResource triggered ===');

		if (id.slice(0, 4) !== 'new_') {
			formData.append('id', id);
		}
		// TBD: add validation here - if not all required fields are filled, otherwise cancel
		// and mark the missing fields invalid

		return async ({ result }) => {
			// console.log('=== callback in submit function triggered ===');
			if (result.type === 'success') {
				if (id.slice(0, 4) === 'new_') {
					id = result.data?.id;
					// console.log('=== result.data? ===');
					// console.log(result.data);
					creationDate = result.data?.creationDate;
				}
			}
			// await applyAction(result);
			// update()
		};
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
			<!-- <h5
				class="title-small md:title lg:title-large base-content card-title {edit
					? `ring-2 ring-info`
					: ``}"
				contenteditable="true"
				oninput={(event: Event) => (name = (event.target as HTMLElement).innerText)}
				onblur={() => createOrUpdateResource()}
			>
				{name}
			</h5> -->
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
			<!-- TBD: move this if around the relevant list points,
			if there are any left, that read-only users are also supposed to see. -->
			{#if userRight === 'write' || userRight === 'own'}
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
					<!-- <button id="dropdown-menu-icon" type="button" class="dropdown-toggle btn btn-square btn-text btn-secondary" aria-haspopup="menu" aria-expanded="false" aria-label="Dropdown">
					<span class="icon-[tabler--dots-vertical] size-6"></span>
				</button> -->
					<ul
						class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden shadow-xs"
						role="menu"
						aria-orientation="vertical"
						aria-labelledby="dropdown-menu-icon-{id}"
					>
						<li class="items-center">
							<button
								class="btn dropdown-item btn-text text-base-content content-center justify-start"
								aria-label="Edit Button"
								onclick={() => (edit ? (edit = false) : (edit = true))}
								><span class="icon-[material-symbols--edit-outline-rounded]"></span> Edit</button
							>
						</li>
						{#if userRight === 'own'}
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
									><span class="icon-[tabler--share-2]"></span>Share
									<span class="icon-[tabler--chevron-right] size-4 rtl:rotate-180"></span>
								</button>
								<!-- min-w-60 -->
								<ul
									class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden min-w-[15rem] shadow-xs"
									role="menu"
									aria-orientation="vertical"
									aria-labelledby="share-{id}"
								>
									<!-- <li> -->
										<!-- <form method="POST" use:enhance={() => dropdownMenu?.classList.add('hidden')}> -->
										<!-- <form method="POST" use:enhance> -->
									{#if microsoftTeams}
										<form
											method="POST"
											name="shareForm-resource-{id}"
											use:enhance={async () => {
												// console.log('=== share form submitted - closing the dropdown ===');
												dropdownShareDropdown?.close();
												dropdownMenu?.close();
												// dropdownMenu?.close()
												// const { HSDropdown } = await import('flyonui/flyonui.js');
												// if(dropdownMenu){
												// 	HSDropdown.close(dropdownMenu)
												// }
											}}
										>
											{#each microsoftTeams.sort((a, b) => a.displayName.localeCompare(b.displayName)) as team (team.id)}
												<li>
													<div class="flex items-center">
														<!-- Also send the desired action for the share: own, write, read.
												Pass information if access_policy already exists to form handling function share(). -->
														<!-- <button
															data-sveltekit-preload-data={false}
															class="btn dropdown-item btn-text max-w-40 content-center"
															name="id"
															value={id}
															formaction="?/share&teamid={team.id}"
															><span class="icon-[fluent--people-team-16-filled]"
															></span>{team.displayName.slice(0, 8)}{team.displayName.length > 9
																? ' ...'
																: null}
														</button> -->
														<div class="dropdown-item max-w-40 content-center">
															<span class="icon-[fluent--people-team-16-filled]"
															></span>{team.displayName.slice(0, 8)}{team.displayName.length > 9
																? ' ...'
																: null}
														</div>
														<div class="mr-2">
															<!-- {rightsIconSelection(team.id) ? "bg-success" : ""} -->
															<span class="{iconMapping(accessAction(team.id))} size-4"></span>
														</div>
														<div
															class="dropdown bg-base-300 relative inline-flex [--offset:0] [--placement:left-start]"
														>
															<ul
																class="dropdown-menu bg-base-300 outline-outline dropdown-open:opacity-100 hidden outline-2"
																role="menu"
																aria-orientation="vertical"
																aria-labelledby="rights-{id}"
															>
																<li>
																	<button
																		data-sveltekit-preload-data={false}
																		class="btn dropdown-item btn-text max-w-40 content-center"
																		name="id"
																		value={id}
																		formaction="?/share&identityid={team.id}&action=own"
																		type="submit"
																		onclick={() => {
																			teamRight = 'own';
																		}}
																		aria-label="own"
																		><span class="icon-[tabler--key-filled] bg-success"
																		></span></button
																	>
																</li>
																<li>
																	<button
																		data-sveltekit-preload-data={false}
																		class="btn dropdown-item btn-text max-w-40 content-center"
																		name="id"
																		value={id}
																		formaction="?/share&identityid={team.id}&action=write"
																		type="submit"
																		onclick={() => {
																			teamRight = 'write';
																		}}
																		aria-label="write"
																		><span
																			class="icon-[material-symbols--edit-outline-rounded] bg-warning"
																		></span>
																	</button>
																</li>
																<li>
																	<button
																		data-sveltekit-preload-data={false}
																		class="btn dropdown-item btn-text max-w-40 content-center"
																		name="id"
																		value={id}
																		formaction="?/share&identityid={team.id}&action=read"
																		type="submit"
																		onclick={() => {
																			teamRight = 'read';
																		}}
																		aria-label="read"
																		><span class="icon-[tabler--eye] bg-neutral"></span>
																	</button>
																</li>
																<li>
																	<button
																		data-sveltekit-preload-data={false}
																		class="btn dropdown-item btn-text max-w-40 content-center"
																		name="id"
																		value={id}
																		formaction="?/share&identityid={team.id}&action=unshare"
																		onclick={() => {
																			dropdownShareDropdown?.close();
																			dropdownMenu?.close();
																		}}
																		type="submit"
																		aria-label="remove share"
																		><span class="icon-[tabler--ban] bg-error"></span>
																	</button>
																</li>
															</ul>
															<button
																id="rights-{id}"
																type="button"
																class="dropdown-toggle btn btn-text bg-base-300"
																aria-haspopup="menu"
																aria-expanded="false"
																aria-label="Dropdown"
															>
																<span
																	class="icon-[tabler--chevron-down] dropdown-open:rotate-180 size-4"
																></span>
															</button>
														</div>
														<!-- <div class={rightsIconSelection(team.id) ? 'block' : 'invisible'}>
															<span class="icon-[openmoji--check-mark]"></span>
														</div> -->
													</div>
												</li>
												<!-- TBD: add aria-label: aria-label={team ? team : 'Team'} -->
											{/each}
											<li class="dropdown-footer gap-2">
												<button
													class="btn dropdown-item btn-text text-base-content content-center justify-start"
													>... more options</button
												>
											</li>
										</form>
									{/if}
									<!-- </li> -->
									<!-- <li>
								Second
							</li> -->
								</ul>
							</li>
							<li class="dropdown-footer gap-2">
								<!-- TBD: refactor into a call to same route and handle with params in load function 
						either by changing to method="GET" or by using a link instead of a button inside a form-->
								<form method="POST" use:enhance={() => card.remove()}>
									<button
										class="btn dropdown-item btn-error btn-text content-center justify-start"
										aria-label="Delete Button"
										name="id"
										value={id}
										formaction="?/delete"><span class="icon-[tabler--trash]"></span>Delete</button
									>
								</form>
								<!-- onclick={deleteResource} -->
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
		<!-- {#if form?.status == 'created'}
			Successfully created resource - remove this message again
		{/if} -->
		<p class="body-small md:body text-primary-container-content">
			{description || 'No description available'}
		</p>
	{/if}
</Card>

{#snippet footer()}
	<div class="card-actions flex justify-between">
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
				class="btn-success-container btn btn-circle btn-gradient"
				onclick={() => (edit = false)}
				aria-label="Done"
			>
				<span class="icon-[mingcute--check-2-fill]"></span>
			</button>
		{/if}
	</div>
{/snippet}
