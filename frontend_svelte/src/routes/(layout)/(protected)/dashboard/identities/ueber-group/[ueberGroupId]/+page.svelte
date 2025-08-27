<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import JsonData from '$components/JsonData.svelte';
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	// const { data, ...pageWithoutData } = page;
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { Group, Hierarchy } from '$lib/types';
	import Card from '$components/Card.svelte';
	import IdentityListItem from '../../IdentityListItem.svelte';
	import { crossfade } from 'svelte/transition';
	let { data }: { data: PageData } = $props();

	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		if (debug) {
			goto(`?debug=true`, { replaceState: true });
		} else {
			goto(`?`, { replaceState: true });
		}
	});

	const groupConnection: SocketioConnection = {
		namespace: '/group',
		cookie_session_id: page.data.session.sessionId
		// query_params: {
		// 	'request-access-data': true,
		// }
	};

	let ueberGroup = $state(data.thisUeberGroup);

	// const shortUeberGroupName = () => {
	// 	let shortName = ueberGroup?.name.slice(0, 15) || 'this UeberGroup';
	// 	if (ueberGroup && ueberGroup?.name.length > 15) {
	// 		shortName = shortName + '...';
	// 	}
	// 	return shortName;
	// };

	let linkedGroups = $state<Group[]>(data.thisUeberGroup?.groups || []);
	let allGroups = $state<Group[]>(data.allOtherGroups || []);
	const [sendGroupCrossfade, receiveGroupCrossfade] = crossfade({ duration: 400 });
	const newGroup = $state<Group>({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		name: '',
		description: ''
	});
	let newGroupInherit = $state(true);
	let existingGroupInherit = $state(true);
	const socketioGroup = new SocketIO(groupConnection, () => allGroups);

	socketioGroup.client.emit('read');
	socketioGroup.client.on('transferred', (data: Group) => {
		if (!linkedGroups.some((group) => group.id === data.id)) {
			socketioGroup.handleTransferred(data);
		}
	});
	socketioGroup.client.on('deleted', (resource_id: string) => {
		// socketioGroup.handleDeleted(resource_id)
		linkedGroups = linkedGroups.filter((group) => group.id !== resource_id);
	});
	socketioGroup.client.on('status', (status: SocketioStatus) => {
		if ('success' in status) {
			if (status.success === 'created') {
				if (status.submitted_id === newGroup.id) {
					linkedGroups.push({ ...newGroup, id: status.id });
					newGroup.id = 'new_' + Math.random().toString(36).substring(2, 9);
					newGroup.name = '';
					newGroup.description = '';
				}
			} else if (status.success === 'linked') {
				linkedGroups.push(allGroups.find((group) => group.id === status.id) as Group);
				allGroups = allGroups.filter((group) => group.id !== status.id);
			} else if (status.success === 'unlinked') {
				allGroups.push(linkedGroups.find((group) => group.id === status.id) as Group);
				linkedGroups = linkedGroups.filter((group) => group.id !== status.id);
			}
		}
	});

	const addNewGroup = () => {
		// TBD: make inherit a parameter in the form.
		socketioGroup.submitEntity(newGroup, ueberGroup?.id, newGroupInherit);
	};

	const linkGroup = (groupId: string) => {
		if (ueberGroup) {
			const hierarchy: Hierarchy = {
				child_id: groupId,
				parent_id: ueberGroup.id,
				inherit: existingGroupInherit
			};
			socketioGroup.linkEntities(hierarchy);
		}
	};

	const unlinkGroup = (groupId: string) => {
		if (ueberGroup) {
			const hierarchy: Hierarchy = {
				child_id: groupId,
				parent_id: ueberGroup.id
			};
			socketioGroup.unlinkEntities(hierarchy);
		}
	};

	const deleteGroup = (groupId: string) => {
		// TBD: unlink before (or after) delete?
		socketioGroup.deleteEntity(groupId);
	};
</script>

<div class="flex flex-row">
	<a href="../">
		<button class="btn btn-accent-container">
			<span class="icon-[tabler--chevron-left]"></span>
			Back to all identities
		</button>
	</a>
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base" for="debug-switcher">Debug: </label>
		<input id="debug-switcher" type="checkbox" class="switch-neutral switch" bind:checked={debug} />
	</div>
</div>

{#snippet newGroupHeader()}
	<h5 class="title-small md:title lg:title-large text-base-content card-title">
		New group for {ueberGroup?.name || 'this UeberGroup'}
	</h5>
{/snippet}

{#snippet existingGroupsHeader()}
	<h5 class="title-small md:title lg:title-large text-base-content card-title">
		Add existing group to {ueberGroup?.name || 'this UeberGroup'}
		<p class="title text-base-content card-title text-center">
			Click on a group to add to this UeberGroup.
		</p>
		<div class="mb-2 flex flex-1 items-center gap-1">
			<label class="label label-text text-base" for="new_group-inherit"
				>Inherit rights from {ueberGroup?.name || 'this UeberGroup'}:
			</label>
			<input
				id="new_group-inherit"
				type="checkbox"
				class="switch-info switch"
				bind:checked={existingGroupInherit}
			/>
		</div>
	</h5>
{/snippet}

{#snippet linkedGroupsHeader()}
	<h5 class="title-small md:title lg:title-large text-base-content card-title">
		Groups in {ueberGroup?.name || 'this UeberGroup'}
	</h5>
{/snippet}

{#if ueberGroup}
	<Heading>{ueberGroup.name}</Heading>
	<p class="title text-base-content card-title py-4 text-center">{ueberGroup.description}</p>

	{#if debug}
		<JsonData data={ueberGroup} />
	{/if}

	<div class="grid grid-cols-1 justify-around gap-4 pb-4 md:grid-cols-2">
		<Card id={newGroup.id} extraClasses="max-h-80" header={newGroupHeader}>
			<div class="w-full overflow-x-auto">
				<div class="input-filled input-base-content mb-2 w-fit grow">
					<input
						id="new-group-name"
						type="text"
						placeholder="Name the demo resource"
						class="input input-sm md:input-md shadow-shadow shadow-inner"
						name="group-name"
						bind:value={newGroup.name}
					/>
					<label class="input-filled-label" for="new-group-name">Name</label>
				</div>
				<div class="textarea-filled textarea-base-content w-full">
					<textarea
						id="new-group-description"
						class="textarea shadow-shadow shadow-inner"
						placeholder="Describe the demo resource here."
						name="groupdescription"
						bind:value={newGroup.description}
					>
					</textarea>
					<label class="textarea-filled-label" for="new-group-description"> Description </label>
				</div>
				<!-- TBD: make snippet and put into footer -->
				<div class="flex h-11 flex-row">
					<div class="mb-2 flex flex-1 items-center gap-1">
						<label class="label label-text text-base" for="existing_group-inherit"
							>Inherit rights from {ueberGroup?.name || 'this UeberGroup'}:
						</label>
						<input
							id="existing_group-inherit"
							type="checkbox"
							class="switch-info switch"
							bind:checked={newGroupInherit}
						/>
					</div>
					<button
						class="btn-success-container btn btn-circle btn-gradient shadow-outline shrink shadow-md"
						aria-label="Send Icon Button"
						onclick={() => addNewGroup()}
						data-overlay="#add-ueber-group-modal"
					>
						<span class="icon-[tabler--send-2]"></span>
					</button>
				</div>
			</div>
		</Card>
		{#if debug}
			<JsonData data={newGroup} />
		{/if}
		<div>
			<Card id="existing-groups" header={existingGroupsHeader}>
				<dl class="divider-outline divide-y">
					{#if allGroups !== undefined && allGroups.length > 0}
						{#each allGroups as group (group.id)}
							<div
								in:receiveGroupCrossfade={{ key: group }}
								out:sendGroupCrossfade={{ key: group }}
							>
								<IdentityListItem identity={group} link={linkGroup} />
							</div>
						{/each}
					{:else}
						<div
							class="alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
							role="alert"
						>
							No Groups found for this user.
						</div>
					{/if}
				</dl>
			</Card>
		</div>
		{#if debug}
			<JsonData data={allGroups} />
		{/if}
	</div>

	<div class={debug ? 'grid grid-cols-2 justify-around gap-4 pb-4' : ''}>
		<Card id="linked-groups" header={linkedGroupsHeader}>
			<dl class="divider-outline divide-y">
				{#if linkedGroups !== undefined && linkedGroups.length > 0}
					{#each linkedGroups as group (group.id)}
						<div in:receiveGroupCrossfade={{ key: group }} out:sendGroupCrossfade={{ key: group }}>
							<IdentityListItem identity={group} unlink={unlinkGroup} remove={deleteGroup} />
						</div>
					{/each}
				{:else}
					<div
						class="alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
						role="alert"
					>
						No Groups found for in this ueber-group.
					</div>
				{/if}
			</dl>
		</Card>
		{#if debug}
			<JsonData data={linkedGroups} />
		{/if}
	</div>

	<ul class="title bg-warning-container/80 text-warning-container-content mt-4 rounded-2xl">
		<li>Add tests for link and unlink functionality and status.</li>
		<li>
			Check if there is a "hierarchy read" anywhere, otherwise implement a read_relations in
			BaseCRUD
		</li>
		<li>
			In BaseCRUD, delete Access policies and hierarchies (based on child_id) when deleting an
			entity.
		</li>
	</ul>
	<ul class="title bg-warning-container/60 text-warning-container-content mt-4 rounded-2xl">
		<li>Add a "multi-create" to new group card with numerical index at the end</li>
	</ul>
	<ul class="title bg-warning-container/40 text-warning-container-content mt-4 rounded-2xl">
		<li>Maybe: debug crossfade in connection with empty lists?</li>
		<li>Add the modify / edit functionality.</li>
	</ul>
{:else}
	<Heading>Error</Heading>
	<p>No Ueber Group found.</p>
{/if}

<p class="title bg-warning-container/20 text-warning-container-content mt-4 rounded-2xl">
	For resource hierarchies (protected resources) also add the order functionality by drag and drop.
</p>

<!-- <JsonData data={pageWithoutData} /> -->
