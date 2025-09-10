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
	import IdBadge from '../../../IdBadge.svelte';
	import { crossfade } from 'svelte/transition';
	import { SvelteMap } from 'svelte/reactivity';
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
	let newMultipleGroups = $state(false);
	let multipleGroupsSuffixes = $state({ start: 1, end: 2 });
	let newGroupIdsSuffixes = new SvelteMap([[newGroup.id, '']]);
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
				// console.log('=== newGroup ===');
				// console.log($state.snapshot(newGroup));
				// console.log('=== status ===');
				// console.log(status);
				// console.log('=== newGroupIdsSuffixes ===');
				// console.log(newGroupIdsSuffixes);
				if (newGroupIdsSuffixes.has(status.submitted_id)) {
					// console.log('=== match for submitted_id ===');
					// if (status.submitted_id === newGroup.id) {
					const suffix = newGroupIdsSuffixes.get(status.submitted_id);
					const thisGroup: Group = Object.assign({}, newGroup);
					thisGroup.name = newGroup.name + suffix;
					linkedGroups.push({ ...thisGroup, id: status.id });
					newGroupIdsSuffixes.delete(status.submitted_id);
					if (suffix === '' || newGroupIdsSuffixes.size === 1) {
						newGroup.name = '';
						newGroup.description = '';
						if (suffix === '') {
							newGroup.id = 'new_' + Math.random().toString(36).substring(2, 9);
							newGroupIdsSuffixes.set(newGroup.id, '');
						}
					}
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
		if (newMultipleGroups) {
			for (
				let suffix = multipleGroupsSuffixes.start;
				suffix <= multipleGroupsSuffixes.end;
				suffix++
			) {
				const thisGroup = Object.assign({}, newGroup);
				thisGroup.id = 'new_' + Math.random().toString(36).substring(2, 9);
				thisGroup.name = thisGroup.name + `_${suffix}`;
				newGroupIdsSuffixes.set(thisGroup.id, `_${suffix}`);
				socketioGroup.submitEntity(thisGroup, ueberGroup?.id, newGroupInherit);
			}
		} else {
			socketioGroup.submitEntity(newGroup, ueberGroup?.id, newGroupInherit);
		}
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
		<label class="label label-text text-base-content" for="debug-switcher">Debug: </label>
		<input id="debug-switcher" type="checkbox" class="switch-neutral switch" bind:checked={debug} />
	</div>
</div>

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
			bind:value={newGroup.name}
		/>
		<label class="input-filled-label" for="new-group-name">Name</label>
	</div>
{/snippet}

{#snippet existingGroupsHeader()}
	<h5 class="title-small md:title lg:title-large text-base-content card-title">
		Add existing group to {ueberGroup?.name || 'this UeberGroup'}
		<p class="title text-base-content card-title text-center">
			Click on a group to add to this UeberGroup.
		</p>
		<div class="mb-2 flex flex-1 items-center gap-1">
			<label class="label label-text text-base-content" for="new_group-inherit"
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
	<Heading>{ueberGroup.name}<IdBadge id={ueberGroup.id} /></Heading>
	<p class="title text-base-content card-title py-4 text-center">{ueberGroup.description}</p>

	{#if debug}
		<JsonData data={ueberGroup} />
	{/if}

	<div class="grid grid-cols-1 justify-around gap-4 pb-4 md:grid-cols-2">
		<Card id={newGroup.id} extraClasses="max-h-80" header={newGroupHeader}>
			<div class="w-full overflow-x-auto">
				{#if newMultipleGroups}
					<div class="flex flex-row items-end">
						{@render newGroupNameField()}
						<span class="flex-1 pb-3">{newGroupSuffix}</span>
					</div>
				{:else}
					{@render newGroupNameField()}
				{/if}
				<!-- <div class="input-filled input-base-content mb-2 {newMultipleGroups ? '' : ''}">
					<input
						id="new-group-name"
						type="text"
						placeholder="Name the demo resource"
						class="input input-sm md:input-md shadow-shadow flex-1 shadow-inner"
						name="group-name"
						bind:value={newGroup.name}
					/>
					<label class="input-filled-label" for="new-group-name">Name</label>
					<span class="flex-1">test{newGroupSuffix}</span>
				</div> -->
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
						<label class="label" for="multiple-new-groups">Add multiple groups with suffix </label>
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
			<div class="flex flex-col gap-2">
				<p>newGroup</p>
				<JsonData data={newGroup} />
				<button class="btn btn-secondary-container" onclick={() => console.log(newGroupIdsSuffixes)}
					>newGroupIdsSuffixes -> console</button
				>
				<!-- <p>newGroupIdsSuffixes</p>
				<JsonData data={newGroupIdsSuffixes} /> -->
			</div>
		{/if}
		<div>
			<Card id="existing-groups" header={existingGroupsHeader}>
				<dl class="divider-outline divide-y">
					{#if allGroups !== undefined && allGroups.length > 0}
						{#each allGroups as group (group.id)}
							<!-- TBD: debug crossfade in connection with empty lists -->
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
		<li>Add a "multi-create" to new group card with numerical index at the end</li>
		<li>Add the modify / edit functionality.</li>
	</ul>
{:else}
	<Heading>Error</Heading>
	<p>No Ueber Group found.</p>
{/if}

<p class="title bg-warning-container/60 text-warning-container-content mt-4 rounded-2xl">
	For resource hierarchies (protected resources) also add the order functionality by drag and drop.
</p>

<!-- <JsonData data={pageWithoutData} /> -->
