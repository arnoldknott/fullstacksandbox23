<script lang="ts">
	import type { User as MicrosoftUser } from '@microsoft/microsoft-graph-types';
	import { onDestroy, onMount } from 'svelte';
	import { SvelteMap } from 'svelte/reactivity';
	import { crossfade } from 'svelte/transition';

	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	import { IdentityType } from '$lib/accessHandler';
	import { SocketIO, type SocketioConnection } from '$lib/socketio.svelte';
	import type { Group, UeberGroup } from '$lib/types';

	import IdBadge from '../../../IdBadge.svelte';
	import IdentityListItem from '../../IdentityListItem.svelte';
	import type { PageData } from './$types';

	// Page related stuff:
	let { data }: { data: PageData } = $props();
	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		if (debug) {
			goto(`?debug=true`, { replaceState: true });
		} else {
			goto(`?`, { replaceState: true });
		}
	});

	// Data variables for Ueber-Groups and Groups:
	let ueberGroup = $derived(data.thisUeberGroup);
	let editUeberGroup = $state(false);

	// const shortUeberGroupName = () => {
	// 	let shortName = ueberGroup?.name.slice(0, 15) || 'this UeberGroup';
	// 	if (ueberGroup && ueberGroup?.name.length > 15) {
	// 		shortName = shortName + '...';
	// 	}
	// 	return shortName;
	// };

	let socketioUeberGroup: SocketIO<UeberGroup> = $state()!;
	let socketioGroup: SocketIO<Group> = $state()!;
	// let groupsRelation: Relation = $state()!;
	let linkedGroups = $derived<Group[]>(
		socketioGroup?.getSelectedEntities('linkedToUeberGroup') || []
	);
	let unlinkedGroups = $derived<Group[]>(
		socketioGroup?.getSelectedEntities('notLinkedToUeberGroup') || []
	);
	const [sendGroupCrossfade, receiveGroupCrossfade] = crossfade({ duration: 400 });
	// const [sendIdentityCrossfade, receiveIdentityCrossfade] = crossfade({ duration: 400 });
	let newGroupInherit = $state(true);
	let existingGroupInherit = $state(true);
	let newMultipleGroups = $state(false);
	let multipleGroupsSuffixes = $state({ start: 1, end: 2 });
	let newGroupSuffix = $derived(
		newMultipleGroups
			? '_[' + multipleGroupsSuffixes.start + ':' + multipleGroupsSuffixes.end + ']'
			: null
	);
	$effect(() => {
		if (multipleGroupsSuffixes.end <= multipleGroupsSuffixes.start) {
			multipleGroupsSuffixes.end = multipleGroupsSuffixes.start + 1;
		}
	});

	// SocketIO for Ueber-Groups and Groups:
	const ueberGroupConnection: SocketioConnection = {
		namespace: '/ueber-group',
		sessionId: page.data.session.sessionId
	};

	// TBD: when porting to group,
	// remember to request the data of this group
	// via resource-ids,
	// as there is only read(id) callback-on-connect!

	// Group related stuff:
	const groupConnection: SocketioConnection = {
		namespace: '/group',
		sessionId: page.data.session.sessionId,
		parentId: page.params.ueberGroupId,
		queryParams: {
			'request-access-data': true
		}
	};
	onMount(() => {
		socketioUeberGroup = new SocketIO<UeberGroup>(ueberGroupConnection, {
			transferred: false,
			deleted: false
		});

		socketioUeberGroup.client.on('deleted', (resource_id: string) => {
			if (ueberGroup && ueberGroup.id === resource_id) {
				goto('../');
			}
		});

		socketioUeberGroup.client.on('transferred', (data: UeberGroup) => {
			if (ueberGroup && ueberGroup.id === data.id) {
				ueberGroup = data;
			}
		});

		socketioGroup = new SocketIO<Group>(groupConnection, {
			template: { name: '', description: '' }
		});
		socketioGroup.client.emit('read');
		// socketioGroup.createPending();

		socketioGroup.createLinkedSelection('linkedToUeberGroup');
		socketioGroup.createLinkedSelection('notLinkedToUeberGroup', true);

		// const ueberGroupRelations = new RelationHandler<UeberGroup>(() => ueberGroup);
		// groupsRelation = ueberGroupRelations.addChild(
		// 	'groups',
		// 	socketioGroup,
		// 	() => data.thisUeberGroup?.groups,
		// 	true
		// );
	});
	$effect(() => {
		// Seed from Rest-API data on initial load, then keep in sync via SocketIO.
		socketioGroup.entities = data.allGroups;
	});

	onDestroy(() => {
		socketioUeberGroup?.client.disconnect();
		socketioGroup?.client.disconnect();
	});

	// TBD: refactor to use methods of SocketIO!
	const addNewGroup = () => {
		const parentId = ueberGroup?.id;
		const basePendingGroup = socketioGroup?.pendingEntities[0];
		if (!parentId || !basePendingGroup) return;

		const submitGroup = (overrides: Partial<Group>, inherit: boolean) => {
			const pendingGroup = socketioGroup.createPending(overrides);
			socketioGroup.submitEntity(pendingGroup, parentId, inherit);
		};

		if (newMultipleGroups) {
			for (let s = multipleGroupsSuffixes.start; s <= multipleGroupsSuffixes.end; s++) {
				submitGroup(
					{ ...basePendingGroup, name: `${basePendingGroup.name}_${s}` },
					newGroupInherit
				);
			}
			socketioGroup.createPending();
		} else {
			socketioGroup.submitEntity(undefined, parentId, newGroupInherit);
		}
	};

	// const linkGroup = (groupId: string) => groupsRelation.link(groupId, existingGroupInherit);

	// const unlinkGroup = (groupId: string) => groupsRelation.unlink(groupId);

	const deleteGroup = (groupId: string) => socketioGroup.deleteEntity(groupId);

	// User related stuff:
	let allOtherMicrosoftUsers = $derived<MicrosoftUser[]>(data.allMicrosoftUsers || []);
	let linkedMicrosoftUsers = $derived<MicrosoftUser[]>(data.linkedMicrosoftUsers || []);
	// TBD: rethink this typing - also loosing the local id here and only leaving the azure_user_id as id.
	// Maybe this could be another Map with user.id (from this app) as key and MicrosoftUser as value?
	type LocalMicrosoftUser = {
		id: string;
		name?: string | null;
		mail?: string | null;
	};
	// Pure derived projection: rebuild from sources on every read.
	// No $effect mutation, so writable-derived consumers (template, JsonData) stay in sync.
	// TBD: get the identity handling into entityContainer and use the identities there.
	// TBD: move the mapping of MicrosoftUsers to Identities into "integrations.ts",
	// that are closely related to apis and make these transforamtions happen server-side!
	// => no unnecessary data from other sources (like Microdoft Graph) reaches client side.
	let linkedIdentities = $derived.by(() => {
		const identities = new SvelteMap<Group | LocalMicrosoftUser, IdentityType>();
		for (const group of linkedGroups) {
			identities.set(group, IdentityType.GROUP);
		}
		for (const user of linkedMicrosoftUsers) {
			if (user.id) {
				identities.set(
					{
						id: user.id,
						name: user.displayName,
						mail: user.mail
					},
					IdentityType.USER
				);
			}
		}
		return identities;
	});
</script>

<div class="flex flex-row gap-2 pb-4">
	<a href="../">
		<button class="btn btn-accent-container btn-gradient shadow-outline rounded-full shadow-sm">
			<span class="icon-[tabler--chevron-left]"></span>
			Back to all identities
		</button>
	</a>
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base-content" for="debug-switcher">Debug: </label>
		<input id="debug-switcher" type="checkbox" class="switch-neutral switch" bind:checked={debug} />
	</div>
</div>

{#snippet linkedGroupsHeader()}
	<h5 class="title-small md:title lg:title-large text-base-content card-title">
		Groups and Users in {ueberGroup?.name || 'this UeberGroup'}
	</h5>
{/snippet}

{#if ueberGroup}
	<Display>
		{#if !editUeberGroup}
			{ueberGroup.name + ' '}
		{:else}
			<div class="input-filled input-base-content mb-2">
				<input
					type="text"
					placeholder="Name the Ueber-Group"
					class="input input-lg shadow-shadow heading-small md:heading lg:heading-large text-center shadow-inner"
					id="name-ueber-group"
					name="name"
					bind:value={ueberGroup.name}
				/>
				<label class="input-filled-label" for="name-ueber-group">Name</label>
			</div>
		{/if}
		<IdBadge id={ueberGroup.id} />
	</Display>
	<div class={debug ? 'grid grid-cols-2 justify-around gap-4 pb-4' : ''}>
		<div class="flex flex-col">
			{#if !editUeberGroup}
				<p class="title text-base-content card-title py-4 text-center">{ueberGroup.description}</p>
			{:else}
				<div class="textarea-filled textarea-base-content w-full">
					<textarea
						class="textarea shadow-shadow shadow-inner"
						placeholder="Describe the Ueber-Group here."
						id="description-ueber-group"
						name="description"
						bind:value={ueberGroup.description}></textarea>
					<label class="textarea-filled-label" for="description-ueber-group"> Description </label>
				</div>
			{/if}
			<div class="flex flex-wrap gap-2 py-4">
				<button
					class="btn btn-success-container btn-gradient shadow-outline rounded-full shadow-sm"
					onclick={() => goto('#add-group')}
					><span class="icon-[fa6-solid--plus]"></span> Add Group</button
				>
				<button
					class="btn btn-success-container btn-gradient shadow-outline rounded-full shadow-sm"
					onclick={() => goto('#add-user')}
					><span class="icon-[fa6-solid--plus]"></span> Add User</button
				>
				{#if !editUeberGroup}
					<button
						class="btn btn-warning-container btn-gradient shadow-outline rounded-full shadow-sm"
						onclick={() => (editUeberGroup = true)}
					>
						<span class="icon-[material-symbols--edit-outline-rounded]"></span> Edit Ueber-Group
					</button>
				{:else}
					<button
						class="btn btn-success-container btn-gradient shadow-outline rounded-full shadow-sm"
						onclick={() => {
							editUeberGroup = false;
							socketioUeberGroup.submitEntity(ueberGroup);
						}}
					>
						<span class="icon-[fa6-solid--plus]"></span> Update Ueber-Group
					</button>
				{/if}
				{#if data.session?.currentUser?.azure_token_roles?.find((roles) => roles === 'Admin')}
					<button
						class="btn btn-error-container btn-gradient shadow-outline rounded-full shadow-sm"
						aria-label="Delete Ueber Group"
						onclick={() => {
							socketioUeberGroup.deleteEntity(ueberGroup.id);
						}}
					>
						<span class="icon-[tabler--trash]"></span> Delete Ueber-Group
					</button>
				{/if}
			</div>
		</div>
		{#if debug}
			<JsonData data={ueberGroup} />
		{/if}
	</div>

	<div class={debug ? 'grid grid-cols-2 justify-around gap-4 pb-4' : 'py-4'}>
		<Card id="linked-groups" header={linkedGroupsHeader} extraClasses="shadow-outline shadow-md">
			{#if linkedIdentities?.size > 0}
				<dl class="divider-outline divide-y">
					{#each [...linkedIdentities] as [identity, type] (identity.id)}
						<div
							in:receiveGroupCrossfade={{ key: identity }}
							out:sendGroupCrossfade={{ key: identity }}
						>
							<IdentityListItem
								{identity}
								{type}
								unlink={() => socketioGroup.unlink(identity.id)}
								remove={deleteGroup}
							/>
						</div>
					{/each}
				</dl>
			{:else}
				<div
					class="alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
					role="alert"
				>
					No Groups found for in this ueber-group.
				</div>
			{/if}
		</Card>
		{#if debug}
			<JsonData data={linkedGroups} />
		{/if}
	</div>

	<Heading id="add-group">Add group</Heading>

	{#if debug}
		<div class="grid grid-cols-2">
			<!-- <Title id="socketio-group-entities">SocketIO Group Entities</Title>
			<Title id="socketio-group-pending-entities">SocketIO Group Pending Entities</Title>
			<Title id="socketio-group-access-policies">SocketIO Group Access Policies</Title>
			<Title id="socketio-group-access-rights">SocketIO Group Access Rights</Title> -->
			<Title id="socketio-group-children">SocketIO Group Hierarchies</Title>
			<!-- <JsonData data={socketioGroup?.entities} />
			<JsonData data={socketioGroup?.pendingEntities} />
			<JsonData data={socketioGroup?.accessPolicies} />
			<JsonData data={socketioGroup?.accessRights} /> -->
			<JsonData data={socketioGroup?.hierarchies} />
		</div>
	{/if}

	{#snippet newGroupHeader()}
		<h5 class="title-small md:title lg:title-large text-base-content card-title">
			New group for {ueberGroup?.name || 'this UeberGroup'}
		</h5>
	{/snippet}

	{#snippet newGroupNameField()}
		<div class="input-filled input-base-content mb-2 {newMultipleGroups ? '' : ''}">
			<input
				id="new-group-name"
				type="text"
				placeholder="Name the demo resource"
				class="input input-sm md:input-md shadow-shadow flex-1 shadow-inner"
				name="group-name"
				bind:value={socketioGroup.pendingEntities[0].name}
			/>
			<label class="input-filled-label" for="new-group-name">Name</label>
		</div>
	{/snippet}

	{#snippet existingGroupsHeader()}
		<h5 class="title-small md:title lg:title-large text-base-content card-title">
			Add existing groups to {ueberGroup?.name || 'this UeberGroup'}
			<p class="title text-base-content card-title text-center">
				Click on a groups to add to this UeberGroup.
			</p>
			<div class="mb-2 flex flex-1 items-center gap-1">
				<label class="label label-text text-base-content" for="new-group-inherit"
					>Inherit rights from {ueberGroup?.name || 'this UeberGroup'}:
				</label>
				<input
					id="new-group-inherit"
					type="checkbox"
					class="switch-info switch"
					bind:checked={existingGroupInherit}
				/>
			</div>
		</h5>
	{/snippet}

	<div class="grid grid-cols-1 justify-around gap-4 pb-4 md:grid-cols-2">
		<Card
			id={socketioGroup?.pendingEntities[0]?.id ?? 'new-group-card'}
			extraClasses="max-h-90"
			header={newGroupHeader}
		>
			{#if socketioGroup?.pendingEntities[0]}
				<div class="w-full overflow-x-auto">
					{#if newMultipleGroups}
						<div class="flex flex-row items-end">
							{@render newGroupNameField()}
							<span class="flex-1 pb-3">{newGroupSuffix}</span>
						</div>
					{:else}
						{@render newGroupNameField()}
					{/if}
					<div class="textarea-filled textarea-base-content w-full">
						<textarea
							id="new-group-description"
							class="textarea shadow-shadow shadow-inner"
							placeholder="Describe the demo resource here."
							name="groupdescription"
							bind:value={socketioGroup.pendingEntities[0].description}></textarea>
						<label class="textarea-filled-label" for="new-group-description"> Description </label>
					</div>
					<!-- TBD: make snippet and put into footer -->
					<div
						class="label-text mb-2 flex flex-1 items-center gap-1 {newGroupInherit
							? 'text-base-content'
							: 'text-base-content/30'}"
					>
						<input
							id="existing_group-inherit"
							type="checkbox"
							class="switch-info switch"
							bind:checked={newGroupInherit}
						/>
						<label class="label" for="existing_group-inherit"
							>Inherit rights from {ueberGroup?.name || 'this UeberGroup'}
						</label>
					</div>
					<div class="flex h-11 flex-row">
						<div
							class="label-text mb-2 flex flex-1 items-center gap-1 {newMultipleGroups
								? 'text-base-content'
								: 'text-base-content/30'}"
						>
							<input
								id="multiple-new-groups"
								type="checkbox"
								class="switch-info switch"
								bind:checked={newMultipleGroups}
							/>
							<label class="label" for="multiple-new-groups"
								>Add multiple groups with suffix
							</label>
							<input
								id="multiple-groups-start"
								type="number"
								placeholder={multipleGroupsSuffixes.start.toString()}
								class="input shadow-shadow flex-2 shadow-inner"
								name="multiple-groups-suffix-start"
								disabled={!newMultipleGroups}
								bind:value={multipleGroupsSuffixes.start}
							/>
							<span class="label flex-1"> to</span>
							<input
								id="multiple-groups-end"
								type="number"
								placeholder={multipleGroupsSuffixes.end.toString()}
								class="input shadow-shadow flex-2 shadow-inner"
								name="multiple-groups-suffix-end"
								disabled={!newMultipleGroups}
								bind:value={multipleGroupsSuffixes.end}
							/>
							<span class="flex-grow"></span>
						</div>
						<button
							class="btn-success-container btn btn-circle btn-gradient shadow-outline shrink shadow-sm"
							aria-label="Send Icon Button"
							onclick={() => addNewGroup()}
							data-overlay="#add-ueber-group-modal"
						>
							<span class="icon-[tabler--send-2]"></span>
						</button>
					</div>
				</div>
			{:else}
				<div class="label text-error">
					<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
				</div>
			{/if}
		</Card>
		{#if debug}
			<div class="flex flex-col gap-2">
				<p>pendingGroup</p>
				<JsonData data={socketioGroup?.pendingEntities[0]} />
			</div>
		{/if}
		<Card id="existing-groups" header={existingGroupsHeader}>
			{#if unlinkedGroups !== undefined && unlinkedGroups.length > 0}
				<dl class="divider-outline divide-y">
					{#each unlinkedGroups as group (group.id)}
						<!-- TBD: debug crossfade in connection with empty lists -->
						<div in:receiveGroupCrossfade={{ key: group }} out:sendGroupCrossfade={{ key: group }}>
							<IdentityListItem
								identity={group}
								link={() => socketioGroup.link(group.id, ueberGroup?.id, existingGroupInherit)}
							/>
						</div>
					{/each}
				</dl>
			{:else}
				<div
					class="alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
					role="alert"
				>
					No Groups found for this user.
				</div>
			{/if}
		</Card>
		{#if debug}
			<JsonData data={unlinkedGroups} />
		{/if}
	</div>

	<Heading id="add-user">Add user</Heading>

	{#snippet existingUserHeader()}
		<h5 class="title-small md:title lg:title-large text-base-content card-title">
			Add existing users to {ueberGroup?.name || 'this UeberGroup'}
			<p class="title text-base-content card-title text-center">
				Click on a users to add to this UeberGroup.
			</p>
			<div class="mb-2 flex flex-1 items-center gap-1">
				<label class="label label-text text-base-content" for="new-group-inherit"
					>Inherit rights from {ueberGroup?.name || 'this UeberGroup'}:
				</label>
				<input
					id="new-group-inherit"
					type="checkbox"
					class="switch-info switch"
					bind:checked={existingGroupInherit}
				/>
			</div>
		</h5>
	{/snippet}

	<div class={debug ? 'grid grid-cols-2 justify-around gap-4 pb-4' : 'py-4'}>
		<Card id="users" header={existingUserHeader}>
			{#if allOtherMicrosoftUsers?.length > 0}
				<dl class="divider-outline divide-y">
					{#each allOtherMicrosoftUsers as user (user.id)}
						<div class="px-4 py-6 text-base sm:flex sm:flex-row sm:gap-4 sm:px-0">
							<dt class="text-base-content title-small flex-1">{user.displayName}</dt>
							<dd class="text-base-content/80 mt-1 flex-2">{user.mail}</dd>
							<!-- TBD: debug crossfade in connection with empty lists -->
							<!-- <div in:receiveUserCrossfade={{ key: user }} out:sendUserCrossfade={{ key: user }}>
						<IdentityListItem identity={user} link={linkUser} /> -->
						</div>
					{/each}
				</dl>
			{:else}
				<div
					class="alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
					role="alert"
				>
					No Users found.
				</div>
			{/if}
		</Card>
		{#if debug}
			<JsonData data={allOtherMicrosoftUsers} />
		{/if}
	</div>
{:else}
	<Heading id="error">Error</Heading>
	<p>No Ueber Group found.</p>
{/if}

<ul class="title bg-warning-container/80 text-warning-container-content mt-4 rounded-2xl">
	<li class="p-2">
		Develop Account linking module. Return a SvelteMap with [userId, foreignAccount]
	</li>
	<li class="p-2">
		map foreign accounts into strucutre of fssb23 identities for displaying possibilities, for
		eksample in ShareItems, lists, and so on.
	</li>
	<li class="p-2">Add user to ueber-group.</li>
	<li class="p-2">Turn into components to reuse with groups and subgroups.</li>
</ul>

<ul class="title bg-warning-container/60 text-warning-container-content mt-4 rounded-2xl">
	<li class="p-2">
		For resource hierarchies (protected resources) also add the order functionality by drag and
		drop.
	</li>
</ul>

{#if debug}
	<JsonData data={page} />
{/if}
