<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	import JsonData from '$components/JsonData.svelte';
	import IdentityAccordion from './IdentityAccordion.svelte';
	let { data }: { data: PageData } = $props();

	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		if (debug) {
			goto(`?debug=true`, { replaceState: true });
		} else {
			goto(`?`, { replaceState: true });
		}
	});
</script>

<div>
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
		<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
	</div>
</div>

<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="">
	{#if data.session?.currentUser}
		<IdentityAccordion
			title="My user Profile in this app"
			id={data.session.currentUser.id}
			open={false}
		>
			<JsonData data={data.session?.currentUser} />
		</IdentityAccordion>
	{/if}

	<div>
		<div class="title-large m-2">
			Microsoft Teams associated with this fullstack sandbox application
		</div>
		<div class="title-small m-2">
			that {data.session?.microsoftProfile?.displayName || 'current user'} is a member of:
		</div>
	</div>

	{#if data.microsoftTeams.length === 0}
		<div class="alert alert-warning label-large text-center" role="alert">
			No Microsoft Teams found for this user.
		</div>
	{/if}

	{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
		<IdentityAccordion
			icon="icon-[fluent--people-team-16-filled]"
			title={microsoftTeam.displayName || 'Unknown Team'}
			id={microsoftTeam.id || 'random_' + Math.random().toString(36).substring(2, 9)}
		>
			<p class="body">{microsoftTeam.description}</p>
			<a href={microsoftTeam.webUrl} target="_blank" rel="noopener"
				><button class="btn btn-primary-container shadow-outline shadow-md"
					><span class="icon-[bi--microsoft-teams]"></span>Open in Microsoft Teams</button
				></a
			>
			<a href="./identities/msteams/{microsoftTeam.id}"
				><button class="btn btn-info-container shadow-outline shadow-md"
					><span class="icon-[tabler--info-triangle]"></span>More information</button
				></a
			>
			{#if debug}
				<JsonData data={microsoftTeam} />
			{/if}
		</IdentityAccordion>
	{/each}

	<div class="flex w-full flex-row">
		<div class="grow">
			<div class="title-large m-2">
				Ueber-Groups associated with this fullstack sandbox application,
			</div>
			<div class="title-small m-2">
				that {data.session?.microsoftProfile?.displayName || 'current user'} is a member of:
			</div>
		</div>
		{#if data.session?.currentUser?.azure_token_roles?.find((roles) => roles === 'Admin')}
			<button
				class="btn-warning-container btn shadow-outline mr-2 self-center shadow-md"
				aria-haspopup="dialog"
				aria-expanded="false"
				aria-controls="add-element-modal"
				aria-label="Create Ueber Group"
				data-overlay="#add-ueber-group-modal"
			>
				<span class="icon-[material-symbols--edit-outline-rounded]"></span> Create Ueber Group
			</button>

			<div
				id="add-ueber-group-modal"
				class="overlay modal modal-middle overlay-open:opacity-100 hidden"
				role="dialog"
				tabindex="-1"
			>
				<div class="modal-dialog overlay-open:opacity-100">
					<div class="modal-content bg-base-300 shadow-outline shadow">
						<div class="modal-header">
							<h3 class="modal-title">Add new Ueber Group</h3>
							<button
								type="button"
								class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
								aria-label="Close"
								data-overlay="#add-ueber-group-modal"
							>
								<span class="icon-[tabler--x] size-4"></span>
							</button>
						</div>
						<div class="modal-body">
							<div class="w-full overflow-x-auto">
								<div class="input-filled input-base-content mb-2 w-fit grow">
									<input
										type="text"
										placeholder="Name the demo resource"
										class="input input-sm md:input-md shadow-shadow shadow-inner"
										id="name_id_new_element"
										name="name"
									/>
									<label class="input-filled-label" for="name_id_new_element">Name</label>
								</div>
								<div class="textarea-filled textarea-base-content w-full">
									<textarea
										class="textarea shadow-shadow shadow-inner"
										placeholder="Describe the demo resource here."
										id="description_id_new_element"
										name="description"
									>
									</textarea>
									<label class="textarea-filled-label" for="description_id_new_element">
										Description
									</label>
								</div>
							</div>
						</div>
						<div class="modal-footer">
							<button
								class="btn-warning-container btn btn-circle btn-gradient"
								aria-label="Send Icon Button"
							>
								<span class="icon-[tabler--send-2]"></span>
							</button>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>

	{#if data.ueberGroups.length === 0}
		<div class="alert alert-warning label-large text-center" role="alert">
			No Ueber-Groups found for this user.
		</div>
	{/if}

	{#each data.ueberGroups as uberGroup (uberGroup.id)}
		<IdentityAccordion
			icon="icon-[fa--institution]"
			title={uberGroup.name || 'Unknown Group'}
			id={uberGroup.id}
		>
			<div class="flex gap-2">
				<div class="flex flex-col">
					<p class="body">{uberGroup.description}</p>
					<div class="flex gap-2">
						<a href="./identities/ueber-group/{uberGroup.id}"
							><button class="btn btn-info-container shadow-outline shadow-md"
								><span class="icon-[tabler--info-triangle]"></span>More information</button
							></a
						>
						<button class="btn btn-accent-container shadow-outline shadow-md"
							><span class="icon-[fa6-solid--plus]"></span> Add Group</button
						>
						<button class="btn btn-accent-container shadow-outline shadow-md"
							><span class="icon-[fa6-solid--plus]"></span> Add User</button
						>
					</div>
				</div>
				{#if debug}
					<JsonData data={uberGroup} />
				{/if}
			</div>
		</IdentityAccordion>
	{/each}
</div>
