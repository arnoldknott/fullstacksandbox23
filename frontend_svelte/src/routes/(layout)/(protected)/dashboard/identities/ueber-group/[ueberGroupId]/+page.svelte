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

	let groups = $state<Group[]>(data.thisUeberGroup?.groups || []);
	const socketioGroup = new SocketIO(groupConnection, () => groups);

	socketioGroup.client.on('transferred', (data: Group) => socketioGroup.handleTransferred(data));
	socketioGroup.client.on('deleted', (resource_id: string) =>
		socketioGroup.handleDeleted(resource_id)
	);
	socketioGroup.client.on('status', (status: SocketioStatus) => socketioGroup.handleStatus(status));

	const newGroup = $state<Group>({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		name: '',
		description: ''
	});
</script>

<a href="../">
	<button class="btn btn-accent-container">
		<span class="icon-[tabler--chevron-left]"></span>
		Back to all identities
	</button>
</a>

{#if data.thisUeberGroup}
	<Heading>{data.thisUeberGroup.name}</Heading>
	<p>{data.thisUeberGroup.description}</p>
{:else}
	<Heading>Error</Heading>
	<p>No Ueber Group found.</p>
{/if}

<!-- <JsonData data={pageWithoutData} /> -->
