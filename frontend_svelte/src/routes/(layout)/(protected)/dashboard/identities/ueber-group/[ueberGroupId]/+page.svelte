<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import JsonData from '$components/JsonData.svelte';
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	// const { data, ...pageWithoutData } = page;
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { Group } from '$lib/types';
	import Card from '$components/Card.svelte';
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
	const newGroup = $state<Group>({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		name: '',
		description: ''
	});
	const socketioGroup = new SocketIO(groupConnection, () => allGroups);

	socketioGroup.client.emit('read');
	socketioGroup.client.on('transferred', (data: Group) => socketioGroup.handleTransferred(data));
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
			}
			// socketioGroup.handleStatus(status);
		}
	});

	const addNewGroup = () => {
		// TBD: make inherit a parameter in the form.
		socketioGroup.submitEntity(newGroup, ueberGroup?.id, true);
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
	</h5>
{/snippet}

{#if ueberGroup}
	<Heading>{ueberGroup.name}</Heading>
	<p>{ueberGroup.description}</p>

	<Heading>Add group to {ueberGroup.name}</Heading>
	<div class="grid grid-cols-2 justify-around gap-4">
		<Card id={newGroup.id} header={newGroupHeader}>
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
				<div class="text-right">
					<button
						class="btn-warning-container btn btn-circle btn-gradient"
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
			<Card id={newGroup.id} header={newGroupHeader}>
				<dl class="divider-outline divide-y">
					{#each allGroups as group (group.id)}
						<div class="px-4 py-6 text-base sm:grid sm:grid-cols-2 sm:gap-4 sm:px-0">
							<dt class="text-base-content title-small">
								<a href={`/dashboard/identities/group/${group.id}`}>
									{group.name}
								</a>
							</dt>
							<dd class="text-base-content/80 mt-1 sm:col-span-2 sm:mt-0 md:col-span-1">
								{group.description}
							</dd>
						</div>
						<!-- <div class="divider divider-outline"></div> -->
					{/each}
				</dl>
			</Card>
		</div>
		{#if debug}
			<JsonData data={allGroups} />
		{/if}
	</div>
	<ul class="title bg-warning-container/80 text-warning-container-content mt-4 rounded-2xl">
		<li>Change group list into a table - to allow for title, description and action buttons</li>
		<li>Add a selection list for existing groups and a field for creating a new group.</li>
		<li>Make the selection list drag-and-dropable.</li>
		<li>Add the event to base namespace to add a child to a parent resource.</li>
	</ul>

	<ul>
		{#if linkedGroups !== undefined && linkedGroups.length > 0}
			{#each linkedGroups as group (group.id)}
				<li>
					<a href={`/dashboard/identities/group/${group.id}`}>
						{group.name}
					</a>
					<div class="divider divider-outline"></div>
				</li>
			{/each}
		{:else}
			<li>No groups found in this ueber group.</li>
		{/if}
	</ul>
	{#if debug}
		<JsonData data={linkedGroups} />
	{/if}
	<ul class="title bg-warning-container/60 text-warning-container-content mt-4 rounded-2xl">
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

<p class="title bg-warning-container/40 text-warning-container-content mt-4 rounded-2xl">
	For resource hierarchies (protected resources) also add the order functionality by drag and drop.
</p>

<!-- <JsonData data={pageWithoutData} /> -->
