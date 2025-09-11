<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import IdentityAccordion from './IdentityAccordion.svelte';
	import IdentityListItem from './IdentityListItem.svelte';
	import { AccessHandler, IdentityType } from '$lib/accessHandler';

	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { UeberGroup, UeberGroupExtended } from '$lib/types';
	let { data }: { data: PageData } = $props();

	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	let azureAccountLink = $state({
		azure_user_id: data.session?.currentUser?.azure_user_id,
		azure_tenant_id: data.session?.currentUser?.azure_tenant_id,
		azure_grous: data.session?.currentUser?.azure_groups,
		azure_token_roles: data.session?.currentUser?.azure_token_roles,
		azure_token_groups: data.session?.currentUser?.azure_token_groups
	});
	let memberships = $state({
		ueber_groups: data.session?.currentUser?.ueber_groups,
		groups: data.session?.currentUser?.groups,
		sub_groups: data.session?.currentUser?.sub_groups,
		sub_sub_groups: data.session?.currentUser?.sub_sub_groups
	});
	let userAccount = $state(data.session?.currentUser?.user_account);
	let userProfile = $state(data.session?.currentUser?.user_profile);
	$effect(() => {
		if (debug) {
			goto(`?debug=true`, { replaceState: true });
		} else {
			goto(`?`, { replaceState: true });
		}
	});

	const connection: SocketioConnection = {
		namespace: '/ueber-group',
		cookie_session_id: page.data.session.sessionId
		// query_params: {
		// 	'request-access-data': true,
		// }
	};

	let ueberGroups = $state<UeberGroup[]>(data.ueberGroups);
	const socketio = new SocketIO(connection, () => ueberGroups);

	socketio.client.on('transferred', (data: UeberGroupExtended) => socketio.handleTransferred(data));
	socketio.client.on('deleted', (resource_id: string) => socketio.handleDeleted(resource_id));
	socketio.client.on('status', (status: SocketioStatus) => socketio.handleStatus(status));

	const newUeberGroup = $state<UeberGroup>({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		name: '',
		description: ''
	});
</script>

<div class="flex gap-2 py-4">
	<button
		class="btn btn-secondary-container btn-gradient shadow-outline rounded-full shadow-sm"
		onclick={() => goto('#microsoft-teams')}
		><span class="icon-[tabler--chevron-right]"></span> Microsoft Teams</button
	>
	<button
		class="btn btn-secondary-container btn-gradient shadow-outline rounded-full shadow-sm"
		onclick={() => goto('#ueber-groups')}
		><span class="icon-[tabler--chevron-right]"></span> Ueber Groups</button
	>
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
		<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
	</div>
</div>

<Heading>My user data in this app</Heading>

<div
	class="accordion accordion-bordered bg-primary-container text-primary-container-content shadow-outline-variant mb-5 shadow-lg"
	data-accordion-always-open=""
>
	{#if azureAccountLink.azure_user_id}
		<IdentityAccordion
			title="Azure Account Link"
			id={azureAccountLink.azure_user_id}
			active={false}
		>
			<JsonData data={azureAccountLink} />
		</IdentityAccordion>
	{/if}

	{#if data.session?.currentUser}
		<IdentityAccordion
			title="Group memberships"
			id={`${data.session?.currentUser?.id}-memberships`}
			active={false}
		>
			<JsonData data={memberships} />
		</IdentityAccordion>
	{/if}

	{#if userAccount}
		<IdentityAccordion title="User Account" id={userAccount.id} active={false}>
			<JsonData data={userAccount} />
		</IdentityAccordion>
	{/if}

	{#if userProfile}
		<IdentityAccordion title="User Profile" id={userProfile.id} active={false}>
			<JsonData data={userProfile} />
		</IdentityAccordion>
	{/if}

	{#if data.session?.currentUser}
		<IdentityAccordion title="All data" id={data.session?.currentUser?.id} active={false}>
			<JsonData data={data.session?.currentUser} />
		</IdentityAccordion>
	{/if}
</div>

<Heading id="microsoft-teams">Microsoft Teams</Heading>
<p>
	associated with this fullstack sandbox application, that {data.session?.microsoftProfile
		?.displayName || 'current user'} is a member of:
</p>
<div
	class="accordion accordion-bordered bg-primary-container text-primary-container-content shadow-outline-variant mb-5 shadow-lg"
	data-accordion-always-open=""
>
	{#if data.microsoftTeams.length === 0}
		<div class="alert alert-warning label-large text-center" role="alert">
			No Microsoft Teams found for this user.
		</div>
	{/if}

	{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
		{#snippet microsoftTeamsActions()}
			<!-- <ActionsMicrosoftTeams url={new URL(microsoftTeam.webUrl)} id={microsoftTeam.id} /> -->
			<a
				href={microsoftTeam.webUrl}
				aria-label="Open in Microsoft Teams"
				target="_blank"
				rel="noopener"
			>
				<!-- TBD: consider creating a global style class for btn-fssb-small (with argument color) nad btn-fssb-large (with argument color) -->
				<button
					class="btn btn-primary-container btn-gradient shadow-outline btn-circle shadow-sm"
					aria-label="Open in Microsoft Teams"
				>
					<span class="icon-[bi--microsoft-teams]"></span>
				</button>
			</a>
			<a href="./identities/msteams/{microsoftTeam.id}" aria-label="More information">
				<button
					class="btn btn-info-container btn-gradient shadow-outline btn-circle shadow-sm"
					aria-label="More information"
				>
					<span class="icon-[tabler--info-triangle]"></span>
				</button>
			</a>
		{/snippet}
		<IdentityAccordion
			icon={AccessHandler.identityIcon(IdentityType.MICROSOFT_TEAM)}
			title={microsoftTeam.displayName || 'Unknown Team'}
			id={microsoftTeam.id || 'random_' + Math.random().toString(36).substring(2, 9)}
			actions={microsoftTeamsActions}
		>
			<p class="body">{microsoftTeam.description}</p>
			{#if debug}
				<JsonData data={microsoftTeam} />
			{/if}
		</IdentityAccordion>
	{/each}
</div>

<Heading id="ueber-groups">Ueber-Groups</Heading>
<div class="my-5 flex flex-row justify-between">
	<p>
		that {data.session?.microsoftProfile?.displayName || 'current user'} is a member of:
	</p>
	{#if data.session?.currentUser?.azure_token_roles?.find((roles) => roles === 'Admin')}
		<button
			class="btn-success-container btn btn-gradient shadow-outline mr-2 self-center rounded-full shadow-sm"
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
									placeholder="Name Ueber-Group"
									class="input input-sm md:input-md shadow-shadow shadow-inner"
									id="name-new-ueber-group"
									name="name"
									bind:value={newUeberGroup.name}
								/>
								<label class="input-filled-label" for="name-new-ueber-group">Name</label>
							</div>
							<div class="textarea-filled textarea-base-content w-full">
								<textarea
									class="textarea shadow-shadow shadow-inner"
									placeholder="Describe the Ueber-Group here."
									id="description-new-ueber-group"
									name="description"
									bind:value={newUeberGroup.description}
								>
								</textarea>
								<label class="textarea-filled-label" for="description-new-ueber-group">
									Description
								</label>
							</div>
						</div>
					</div>
					<div class="modal-footer">
						<button
							class="btn-success-container btn btn-circle btn-gradient shadow-outline shadow-sm"
							aria-label="Send Icon Button"
							onclick={() => {
								socketio.submitEntity(newUeberGroup);
								newUeberGroup.id = 'new_' + Math.random().toString(36).substring(2, 9);
								newUeberGroup.name = '';
								newUeberGroup.description = '';
							}}
							data-overlay="#add-ueber-group-modal"
						>
							<span class="icon-[tabler--send-2]"></span>
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
<div
	class="accordion accordion-bordered bg-primary-container text-primary-container-content shadow-outline-variant mb-5 shadow-lg"
	data-accordion-always-open=""
>
	{#if ueberGroups.length === 0}
		<div
			class="alert alert-warning bg-warning-container text-warning-container-content/80 label-large text-center"
			role="alert"
		>
			No Ueber-Groups found for this user.
		</div>
	{/if}

	{#each ueberGroups as ueberGroup (ueberGroup.id)}
		{#snippet ueberGroupsActions()}
			<div class="flex gap-2">
				<a
					href="./identities/ueber-group/{ueberGroup.id}"
					aria-label="More information about {ueberGroup.name}"
					><button
						class="btn btn-info-container btn-gradient shadow-outline btn-circle shadow-sm"
						aria-label="More information about {ueberGroup.name}"
						><span class="icon-[tabler--info-triangle]"></span></button
					></a
				>
				{#if data.session?.currentUser?.azure_token_roles?.find((roles) => roles === 'Admin')}
					<button
						class="btn btn-error-container btn-gradient shadow-outline btn-circle shadow-sm"
						aria-label="Delete Ueber Group {ueberGroup.name}"
						onclick={() => {
							socketio.deleteEntity(ueberGroup.id);
						}}
					>
						<span class="icon-[tabler--trash]"></span>
					</button>
				{/if}
			</div>
		{/snippet}
		<IdentityAccordion
			icon={AccessHandler.identityIcon(IdentityType.UEBER_GROUP)}
			title={ueberGroup.name || 'Unknown Group'}
			id={ueberGroup.id}
			actions={ueberGroupsActions}
		>
			<div class="flex gap-2">
				<div class="flex flex-col">
					<p class="body">{ueberGroup.description}</p>
					{#if ueberGroup.groups && ueberGroup.groups.length > 0}
						<p class="title-small md:title lg:title-large text-base-content pl-5 pt-5">
							Linked Groups
						</p>
						<dl class="divider-outline divide-y">
							{#each ueberGroup.groups as group (group.id)}
								<!-- TBD: debug crossfade in connection with empty lists -->
								<IdentityListItem identity={group} />
							{/each}
						</dl>
					{/if}
				</div>
				{#if debug}
					<JsonData data={ueberGroup} />
				{/if}
			</div>
		</IdentityAccordion>
	{/each}
</div>
