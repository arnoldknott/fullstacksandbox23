<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	// import { SvelteSet } from 'svelte/reactivity';
	import { fade, scale } from 'svelte/transition';

	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import JsonData from '$components/JsonData.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio.svelte';
	import type { DemoResourceExtended } from '$lib/types';
	import { initAccordion } from '$lib/userInterface';

	import IdBadge from '../../IdBadge.svelte';
	import IdentityAccordion from '../../identities/IdentityAccordion.svelte';
	import type { PageData } from './$types';
	import DemoResourceContainer from './DemoResourceContainer.svelte';

	let { data }: { data: PageData } = $props();
	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		if (debug) {
			goto(`?debug=true`, { replaceState: true });
		} else {
			goto(`?`, { replaceState: true });
		}
	});

	let socketio: SocketIO<DemoResourceExtended> = $state()!;
	// let socketio: SocketIO<DemoResourceExtended> = $state(
	// 	undefined as unknown as SocketIO<DemoResourceExtended>
	// );
	// let editIds = new SvelteSet<string>();
	let statusMessages = $state<SocketioStatus[]>([]);
	// onMount(() => {
	// 	const connection: SocketioConnection = {
	// 		namespace: '/demo-resource',
	// 		cookie_session_id: page.data.session.sessionId,
	// 		query_params: {
	// 			'request-access-data': true,
	// 			'identity-ids': data.payload.identities.map((identity) => identity.id).join(','),
	// 			'join-admin-room': 'true'
	// 		}
	// 	};
	// 	// TBD: populate by REST-API call initially?

	// 	socketio = new SocketIO<DemoResourceExtended>(connection, {
	// 		pendingTemplate: () => ({
	// 			name: '',
	// 			description: '',
	// 			access_right: Action.OWN
	// 			// creation_date: new Date(Date.now()) // TBD: Check if this is necessary?
	// 		})
	// 	});
	// let ownedDemoResources: DemoResourceExtended[] = $derived([
	// 	...(socketio?.pendingEntities || []),
	// 	...(socketio?.getSelectedEntities('owner') ?? [])
	// ]);
	let ownedDemoResources: DemoResourceExtended[] = $derived(
		socketio?.getSelectedEntities('owner') || []
	);
	let writeDemoResources: DemoResourceExtended[] = $derived(
		socketio?.getSelectedEntities('write') || []
	);
	let readDemoResources: DemoResourceExtended[] = $derived(
		socketio?.getSelectedEntities('read') || []
	);

	onMount(() => {
		const connection: SocketioConnection = {
			namespace: '/demo-resource',
			sessionId: page.data.session.sessionId,
			queryParams: {
				'request-access-data': true,
				'identity-ids': data.payload.identities.map((identity) => identity.id).join(','),
				'join-admin-room': true
			}
		};

		socketio = new SocketIO<DemoResourceExtended>(connection, {
			snapshot: {
				entities: data.payload.entities,
				cursor: data.payload.cursor
			},
			template: {
				name: '',
				description: '',
				access_right: Action.OWN
			}
		});
		socketio.identities = data.payload.identities;
		socketio.addSelection('editing');
		// socketio.createUserHasSpecificAccessRightSelection('owner', Action.OWN);
		// socketio.createUserHasSpecificAccessRightSelection('write', Action.WRITE);
		// socketio.createUserHasSpecificAccessRightSelection('read', Action.READ);
		socketio.createSortedSelection('sortedDate', 'creation_date', false);
		socketio.createUserHasSpecificAccessRightSelection('owner', Action.OWN, 'sortedDate');
		socketio.createUserHasSpecificAccessRightSelection('write', Action.WRITE, 'sortedDate');
		socketio.createUserHasSpecificAccessRightSelection('read', Action.READ, 'sortedDate');
		// socketio.sortSelection('owner', 'creation_date', false);
		// socketio.sortSelection('write', 'creation_date', false);
		// socketio.sortSelection('read', 'creation_date', false);

		// Extra `status` listener — runs alongside the default one. Maintains the local
		// `statusMessages` log and the `editIds` set across the create round-trip.
		socketio.client.on('status', (data: SocketioStatus) => {
			statusMessages.unshift(data);
			// if ('success' in data && data.success === 'created') {
			// 	// The default handler swaps the preliminary `new_...` id for the real server id
			// 	// in the entities array. Mirror that swap inside `editIds` so editing stays active
			// 	// on the newly created resource.
			// 	if (editIds.has(data.submitted_id)) {
			// 		editIds.delete(data.submitted_id);
			// 		editIds.add(data.id);
			// 	}
			// }
		});

		// Extra `deleted` listener — drop the id from `editIds` once the server confirms deletion.
		// socketio.client.on('deleted', (resource_id: string) => {
		// 	editIds.delete(resource_id);
		// });
	});

	// $effect(() => {
	// 	// ownedDemoResources = [
	// 	// 	...socketio.pendingEntities,
	// 	// 	...socketio.getSelectedEntities('owner').sort(sortResourcesByCreationDate)
	// 	// ];
	// 	// writeDemoResources = socketio.getSelectedEntities('write').sort(sortResourcesByCreationDate);
	// 	// readDemoResources = socketio.getSelectedEntities('read').sort(sortResourcesByCreationDate);
	// 	// ownedDemoResources = socketio.getSelectedEntities('owner');
	// 	ownedDemoResources = [...socketio.pendingEntities, ...socketio.getSelectedEntities('owner')];
	// 	writeDemoResources = socketio.getSelectedEntities('write');
	// 	readDemoResources = socketio.getSelectedEntities('read');
	// 	// console.log('=== length of demo resources in socketio ===', socketio.entities.length);
	// 	// console.log(
	// 	// 	'=== length of owned demo resources in socketio ===',
	// 	// 	socketio.getSelectedEntities('owner').length
	// 	// );
	// 	// console.log(
	// 	// 	'=== length of write demo resources in socketio ===',
	// 	// 	socketio.getSelectedEntities('write').length
	// 	// );
	// 	// console.log(
	// 	// 	'=== length of read demo resources in socketio ===',
	// 	// 	socketio.getSelectedEntities('read').length
	// 	// );
	// });

	// const sortResourcesByCreationDate = (a: DemoResourceExtended, b: DemoResourceExtended) => {
	// 	if (a.creation_date && b.creation_date) {
	// 		const dateA = new Date(a.creation_date);
	// 		const dateB = new Date(b.creation_date);
	// 		return dateB.getTime() - dateA.getTime();
	// 	} else {
	// 		return 0;
	// 	}
	// };

	// let ownedDemoResources: DemoResourceExtended[] = $derived.by(() => {
	// 	if (!socketio) return [];
	// 	const pending = socketio?.pendingEntities;
	// 	const existing = (socketio?.entities ?? [])
	// 		.filter((demoResource) => {
	// 			if (demoResource.access_right === Action.OWN) {
	// 				return demoResource;
	// 			}
	// 		})
	// 		.sort(sortResourcesByCreationDate);
	// 	return [...pending, ...existing];
	// });

	// let writeDemoResources: DemoResourceExtended[] = $derived(
	// 	(socketio?.entities ?? [])
	// 		.filter((demoResource) => {
	// 			if (demoResource.access_right === Action.WRITE) {
	// 				return demoResource;
	// 			}
	// 		})
	// 		.sort(sortResourcesByCreationDate)
	// );

	// let readDemoResources: DemoResourceExtended[] = $derived(
	// 	(socketio?.entities ?? [])
	// 		.filter((demoResource) => {
	// 			if (demoResource.access_right === Action.READ) {
	// 				return demoResource;
	// 			}
	// 		})
	// 		.sort(sortResourcesByCreationDate)
	// );

	onDestroy(() => socketio?.client.disconnect());
</script>

<div class="flex flex-row flex-wrap justify-between">
	<div>
		<div class="mb-2 flex items-center gap-1">
			<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
			<input
				type="checkbox"
				class="switch-neutral switch"
				bind:checked={debug}
				id="debugSwitcher"
			/>
		</div>

		<div class="mb-5">
			<button
				class="btn-neutral-container btn btn-gradient shadow-outline rounded-full shadow-sm"
				aria-label="Add Button"
				onclick={() => {
					if (socketio?.pendingEntities.length === 0) socketio?.createPending();
					if (!ownedDemoResources.includes(socketio.pendingEntities[0])) {
						// ownedDemoResources.unshift(socketio.pendingEntities[0]);
						ownedDemoResources = [socketio.pendingEntities[0], ...ownedDemoResources];
					}
				}}
			>
				<span class="icon-[fa6-solid--plus]"></span> Add
			</button>
		</div>
	</div>

	<div class="flex flex-col gap-1">
		<div class="title-small italic">Current user</div>
		<IdBadge id={data.session?.currentUser?.id} />
		<div class="badge badge-xs badge-secondary label-small shadow-outline shadow">
			{data.session?.microsoftProfile?.mail}
		</div>
	</div>

	<div
		class="h-25 w-100 {debug
			? 'block'
			: 'hidden'} bg-base-150 shadow-outline rounded-lg p-2 shadow-inner"
	>
		<div class="title-small italic">Currently editable</div>
		<div class="divider divider-outline"></div>
		<ul class="h-15 list-inside overflow-y-scroll">
			<!-- {#each editIds as id (id)}
				<li class="label" transition:fade>{id}</li>
			{/each} -->
			{#each socketio?.selections['editing'] as id (id)}
				<li class="label" transition:fade>{id}</li>
			{/each}
		</ul>
	</div>

	<div class="bg-base-150 shadow-outline h-25 w-105 rounded-lg p-2 shadow-inner">
		<div class="title-small italic">Status messages</div>
		<div class="divider divider-outline"></div>
		<ul class="h-15 list-inside overflow-y-scroll">
			{#each statusMessages as message (message)}
				{#if 'error' in message}
					<li class="label p-1" transition:fade>
						<div
							class="bg-error-container text-error-container-content flex h-fit flex-row items-center justify-between rounded-xl px-1"
						>
							<span class="icon-[noto--cross-mark] ml-1 size-3"></span>
							<div class="mr-1 h-fit w-fit text-right">{message.error}</div>
						</div>
					</li>
				{:else if 'success' in message}
					<li class="label p-1" transition:fade>
						<div
							class="bg-success-container text-success-container-content flex h-fit flex-row items-center justify-between rounded-xl px-1"
							transition:scale|global={{ duration: 500, start: 2, opacity: 0 }}
						>
							{#if message.success === 'created'}
								<span class="bg-success-container-content icon-[tabler--check]"></span>
							{:else if message.success === 'updated'}
								<span
									class="bg-success-container-content icon-[material-symbols--edit-outline-rounded]"
								></span>
							{:else if message.success === 'deleted'}
								<span class="bg-success-container-content icon-[tabler--trash]"></span>
							{:else if message.success === 'shared'}
								<span class="bg-success-container-content icon-[ic--outline-share]"></span>
							{:else if message.success === 'unshared'}
								<span class="bg-success-container-content icon-[fe--disabled]"></span>
							{/if}
							<div class="mr-1 w-fit text-right">{message.id}</div>
						</div>
					</li>
				{/if}
			{/each}
		</ul>
	</div>
</div>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-2" id="demoResourcesContainer">
	<div>
		<h3 class="title">
			<span class="icon-[tabler--key-filled] bg-success"></span>
			Demo Resources with owner access: {ownedDemoResources.length}
		</h3>
		{#each ownedDemoResources as demoResource, idx (demoResource.id)}
			<DemoResourceContainer
				bind:edit={
					() => socketio.selections['editing'].some((id) => id === demoResource.id),
					(value) => {
						// if (demoResource.id) {
						const isEditing = socketio.selections['editing'].includes(demoResource.id);
						if (value && !isEditing) socketio.addToSelection('editing', [demoResource.id]);
						else if (!value && isEditing)
							socketio.removeFromSelection('editing', [demoResource.id]);
						// }
					}
				}
				identities={data.payload.identities}
				demoResource={() => ownedDemoResources[idx]}
				{socketio}
			/>
			<!-- bind:demoResource={ownedDemoResources[idx]} -->
			<!-- {demoResource} -->
			<!-- demoResource={ownedDemoResources[idx]} -->
			<!-- // demoResource={() => demoResource} -->
			<div class="px-2 {debug ? 'block' : 'hidden'}">
				<p class="title">🚧 Debug Information 🚧</p>
				<JsonData data={demoResource} />
			</div>
			<div
				class="divider-outline-variant divider {idx === ownedDemoResources.length - 1
					? 'hidden'
					: ''}"
			></div>
		{/each}
	</div>
	<div>
		<div class={debug ? 'block' : 'hidden'}>
			<h3 class="title">Pending Entities:</h3>
			<JsonData data={socketio?.pendingEntities} />
		</div>
		<h3 class="title">
			Identities access to demoresources: {data.payload.identities.length}
		</h3>
		<div
			class="accordion accordion-bordered bg-base-150 shadow-outline-variant shadow-lg"
			data-accordion-always-open="true"
			{@attach initAccordion}
		>
			{#each data.payload.identities as identity (identity.id)}
				<div>
					<IdentityAccordion
						icon={AccessHandler.identityIcon(identity.type)}
						title={identity.name}
						id={identity.id || Math.random().toString(36).substring(2, 9)}
						active={false}
					>
						<div class="bg-success-container mb-2 rounded-xl p-2">
							<p class="title-small text-success-container-content p-2">
								<span class="icon-[tabler--key-filled] bg-success-container-content size-4"></span> Owner
								access
							</p>
							<div class="bg-success text-success-content rounded">Elements here</div>
						</div>
						<div class="bg-warning-container mb-2 rounded-xl p-2">
							<p class="title-small text-warning-container-content p-2">
								<span class="icon-[tabler--key-filled] bg-warning-container-content size-4"></span> Write
								access
							</p>
							<div class="bg-warning text-warning-content rounded">Elements here</div>
						</div>
						<div class="bg-neutral-container mb-2 rounded-xl p-2">
							<p class="title-small text-neutral-container-content p-2">
								<span class="icon-[tabler--eye] bg-neutral-container-content size-4"></span> Write access
							</p>
							<div class="bg-neutral text-neutral-content rounded">Elements here</div>
						</div>
						<div class={debug ? 'block' : 'hidden'}>
							<p class="title">🚧 Debug Information 🚧</p>
							<JsonData data={identity} />
						</div>
					</IdentityAccordion>
				</div>
			{/each}
		</div>
		<!-- <JsonData data={demoResources} /> -->
	</div>
	<div>
		<h3 class="title">
			<span class="icon-[material-symbols--edit-outline-rounded] bg-warning"></span>
			Demo Resources with write access: {writeDemoResources.length}
		</h3>
		{#each writeDemoResources as demoResource, idx (demoResource.id)}
			<DemoResourceContainer demoResource={() => writeDemoResources[idx]} {socketio} />
			<div class="px-2 {debug ? 'block' : 'hidden'}">
				<p class="title">🚧 Debug Information 🚧</p>
				<JsonData data={demoResource} />
			</div>
			<div
				class="divider-outline-variant divider {idx === writeDemoResources.length - 1
					? 'hidden'
					: ''}"
			></div>
		{/each}
	</div>
	<div>
		<h3 class="title">
			<span class="icon-[tabler--eye] bg-neutral"></span>
			Demo Resources with read access: {readDemoResources.length}
		</h3>
		{#each readDemoResources as demoResource, idx (demoResource.id)}
			<DemoResourceContainer demoResource={() => readDemoResources[idx]} />
			<div class="px-2 {debug ? 'block' : 'hidden'}">
				<p class="title">🚧 Debug Information 🚧</p>
				<JsonData data={demoResource} />
			</div>
			<div
				class="divider-outline-variant divider {idx === readDemoResources.length - 1
					? 'hidden'
					: ''}"
			></div>
		{/each}
	</div>
</div>
