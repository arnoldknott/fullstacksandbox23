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

	let linkedGroups = $state<Group[]>(data.thisUeberGroup?.groups || []);
	let allGroups = $state<Group[]>([]);
	const [sendGroupCrossfade, receiveGroupCrossfade] = crossfade({ duration: 500 });
	const newGroup = $state<Group>({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		name: '',
		description: ''
	});
	const socketioGroup = new SocketIO(groupConnection, () => allGroups);

	socketioGroup.client.emit('read');
	socketioGroup.client.on('transferred', (data: Group) => {
		if (!linkedGroups.some((group) => group.id === data.id)) {
			socketioGroup.handleTransferred(data);
		}
	});
	socketioGroup.client.on('deleted', (resource_id: string) =>
		socketioGroup.handleDeleted(resource_id)
	);
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
		socketioGroup.submitEntity(newGroup, ueberGroup?.id, true);
	};

	const linkGroup = (groupId: string) => {
		if (ueberGroup) {
			const hierarchy: Hierarchy = {
				child_id: groupId,
				parent_id: ueberGroup.id
				// inherit: true // TBD: make a checkbox
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
		// if (ueberGroup) {
		// 	socketioGroup.client.emit('delete', {
		// 		id: groupId
		// 	});
		// 	linkedGroups = linkedGroups.filter((group) => group.id !== groupId);
		// }
		console.log('=== ueberGroup - deleting group ===');
		console.log('ueber-group.id:', ueberGroup?.id);
		console.log('group.id:', groupId);
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
		<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
		<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
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
		<!-- TBD: add inherit checkbox -->
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

	<div class="grid grid-cols-2 justify-around gap-4 pb-4">
		<Card id={newGroup.id} extraClasses="max-h-80" header={newGroupHeader}>
			<div class="w-full overflow-x-auto">
				<div class="input-filled input-base-content mb-2 w-fit grow">
					<input
						type="text"
						placeholder="Name the demo resource"
						class="input input-sm md:input-md shadow-shadow shadow-inner"
						id="name_id_new_element"
						name="name"
						bind:value={newGroup.name}
					/>
					<label class="input-filled-label" for="name_id_new_element">Name</label>
				</div>
				<div class="textarea-filled textarea-base-content w-full">
					<textarea
						class="textarea shadow-shadow shadow-inner"
						placeholder="Describe the demo resource here."
						id="description_id_new_element"
						name="description"
						bind:value={newGroup.description}
					>
					</textarea>
					<label class="textarea-filled-label" for="description_id_new_element">
						Description
					</label>
				</div>
				<!-- TBD: make snippet and put into footer -->
				<div class="h-11 text-right">
					<button
						class="btn-success-container btn btn-circle btn-gradient shadow-outline shadow-md"
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
								in:receiveGroupCrossfade={{ key: group, duration: 500 }}
								out:sendGroupCrossfade={{ key: group, duration: 500 }}
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
						<div
							in:receiveGroupCrossfade={{ key: group, duration: 500 }}
							out:sendGroupCrossfade={{ key: group, duration: 500 }}
						>
							<IdentityListItem identity={group} unlink={unlinkGroup} remove={deleteGroup} />
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
		{#if debug}
			<JsonData data={linkedGroups} />
		{/if}
	</div>

	<ul class="title bg-warning-container/80 text-warning-container-content mt-4 rounded-2xl">
		<li>Make the selection list crossfade.</li>
		<li>Add tests for link and unlink functionality and status.</li>
	</ul>
	<ul class="title bg-warning-container/60 text-warning-container-content mt-4 rounded-2xl">
		<li>Add a "multi-create" to new group card with numerical index at the end</li>
		<li>Add inherit checkbox to new group card</li>
	</ul>
	<ul class="title bg-warning-container/40 text-warning-container-content mt-4 rounded-2xl">
		<li>Add the modify / edit functionality.</li>
		<li>Add the delete functionality, removing the group from the ueber group.</li>
		<li>
			Also add the delete functionality, deleting the group fully - should also remove from ueber
			group!
		</li>
	</ul>
{:else}
	<Heading>Error</Heading>
	<p>No Ueber Group found.</p>
{/if}

<p class="title bg-warning-container/20 text-warning-container-content mt-4 rounded-2xl">
	For resource hierarchies (protected resources) also add the order functionality by drag and drop.
</p>

<!-- <JsonData data={pageWithoutData} /> -->
