<script lang="ts">
	import { page } from '$app/state';
	// import JsonData from '$components/JsonData.svelte';
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	// const { data, ...pageWithoutData } = page;
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { Group } from '$lib/types';
	let { data }: { data: PageData } = $props();

	const groupConnection: SocketioConnection = {
		namespace: '/ueber-group',
		cookie_session_id: page.data.session.sessionId
		// query_params: {
		// 	'request-access-data': true,
		// }
	};

	let ueberGroup = $state(data.thisUeberGroup);

	let groups = $state<Group[]>(data.thisUeberGroup?.groups || []);
	const socketioGroup = new SocketIO(groupConnection, () => groups);

	socketioGroup.client.on('transferred', (data: Group) => socketioGroup.handleTransferred(data));
	socketioGroup.client.on('deleted', (resource_id: string) =>
		socketioGroup.handleDeleted(resource_id)
	);
	socketioGroup.client.on('status', (status: SocketioStatus) => socketioGroup.handleStatus(status));

	// const newGroup = $state<Group>({
	// 	id: 'new_' + Math.random().toString(36).substring(2, 9),
	// 	name: '',
	// 	description: ''
	// });
</script>

<a href="../">
	<button class="btn btn-accent-container">
		<span class="icon-[tabler--chevron-left]"></span>
		Back to all identities
	</button>
</a>

{#if ueberGroup}
	<Heading>{ueberGroup.name}</Heading>
	<p>{ueberGroup.description}</p>
	<button class="btn btn-accent-container shadow-outline shadow-md"
		><span class="icon-[fa6-solid--plus]"></span> Add Group</button
	>
	<ul class="title bg-warning-container/80 text-warning-container-content mt-4 rounded-2xl">
		<li>Change group list into a table - to allow for title, description and action buttons</li>
		<li>Add a selection list for existing groups and a field for creating a new group.</li>
		<li>Make the selection list drag-and-dropable.</li>
		<li>Add the event to base namespace to add a child to a parent resource.</li>
	</ul>

	<ul>
		{#if ueberGroup.groups !== undefined && ueberGroup.groups.length > 0}
			{#each ueberGroup.groups as group (group.id)}
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
