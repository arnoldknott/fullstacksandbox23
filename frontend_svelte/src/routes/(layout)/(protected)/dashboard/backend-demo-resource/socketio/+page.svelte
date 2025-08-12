<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import { page } from '$app/state';
	import type { AccessPolicy, DemoResourceExtended } from '$lib/types';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';
	import IdentityAccordion from '../../identities/IdentityAccordion.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import DemoResourceContainer from './DemoResourceContainer.svelte';
	import { fade, scale } from 'svelte/transition';
	import IdBadge from '../../IdBadge.svelte';
	import { onDestroy } from 'svelte';

	let { data }: { data: PageData } = $props();
	let editIds = $state(new Set<string>());
	let statusMessages = $state<SocketioStatus[]>([]);
	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		if (debug) {
			goto(`?debug=true`, { replaceState: true });
		} else {
			goto(`?`, { replaceState: true });
		}
	});

	const connection: SocketioConnection = {
		namespace: '/demo-resource',
		cookie_session_id: page.data.session.sessionId,
		query_params: {
			'request-access-data': true,
			'identity-id': data.microsoftTeams.map((team) => team.id).join(',')
		}
	};

	let demoResources = $state<DemoResourceExtended[]>([]);
	// $effect(() => {

	// 	// demoResources = socketio.entities as DemoResourceExtended[];
	// });
	const socketio = new SocketIO(
		connection,
		() => demoResources,
		() => editIds
	);

	// let demoResources = $state(socketio.entities as DemoResourceExtended[]);

	// console.log(
	// 	data.microsoftTeams
	// 		.filter((team) => team.id)
	// 		.map((team) => {
	// 			return {
	// 				id: team.id,
	// 				name: team.displayName || 'Unknown Team',
	// 				type: IdentityType.MICROSOFT_TEAM,
	// 				accessRight: undefined
	// 			};
	// 		})
	// );

	// let identities: Identity[] | undefined = $derived.by(() =>
	// 	data.microsoftTeams
	// 		.filter((team) => team.id)
	// 		.map((team) => {
	// 			return {
	// 				id: team.id,
	// 				name: team.displayName || 'Unknown Team',
	// 				type: IdentityType.MICROSOFT_TEAM,
	// 				accessRight: undefined
	// 			};
	// 		})
	// );

	socketio.receivers();
	$effect(() => {
		// socketio.receivers();
		// socketio.client.on('transfer', (data: DemoResourceExtended) => {
		// 	// if (debug) {
		// 	// 	console.log(
		// 	// 		'=== dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
		// 	// 	);
		// 	// 	console.log(data);
		// 	// }
		// 	if (demoResources.some((res) => res.id === data.id)) {
		// 		// Update existing resource
		// 		demoResources = demoResources.map((res) =>
		// 			// only replaces the keys, where the newly incoming data is defined.
		// 			res.id === data.id ? { ...res, ...data } : res
		// 		);
		// 		// TBD: examin the workflow: access policies of recently changed accesses in resources change the icon,
		// 		// but the data, e.g. in debugging information stays outdated!
		// 	} else {
		// 		// Add new resource
		// 		demoResources.push(data);
		// 	}
		// });
		socketio.client.on('deleted', (resource_id: string) => {
			if (debug) {
				console.log(
					'=== dashboard - backend-demo-resource - socketio - +page.svelte - deleted DemoResources ==='
				);
				console.log(resource_id);
			}
			// if (editIds.has(resource_id)) {
			// 	console.log('=== socketio - deleted receiver - deleting resource from editIds ===');
			editIds.delete(resource_id);
			editIds = new Set(editIds); // trigger reactivity
			// }
			// 	demoResources = demoResources.filter((res) => res.id !== resource_id);
		});
		socketio.client.on('status', (data: SocketioStatus) => {
			statusMessages.unshift(data);
			if (debug) {
				console.log(
					'=== dashboard - backend-demo-resource - socketio - +page.svelte - received status update ==='
				);
				console.log('Status update:', data);
			}
			if ('success' in data) {
				if (data.success === 'created') {
					// 		demoResources.forEach((demoResource) => {
					// 			if (demoResource.id === data.submitted_id) {
					// 				demoResource.id = data.id;
					// 			}
					// 		});
					editIds.add(data.id); // keep editing on after newly created resources
					editIds = new Set(editIds); // trigger reactivity
					// 	} else if (data.success === 'shared') {
					// 		socketio.client.emit('read', data.id);
					// 	} else if (data.success === 'unshared') {
					// 		// TBD: consider not to emit read, but to remove the resource from the list!
					// 		socketio.client.emit('read', data.id);
					// 		// Re-read to see, if there is still access to the resource any other way.
					// 		// If that fails, remove it from the list
					// 		// rerun check on access policies for this resource after removing the unshared policy:
					// 		// TBD: reload all access for the resource,
					// 		// as other users access_policies are still part of the resource, e.g. admin, that created it.
					// 		// however that does not give the current user access any more!
					// 		// demoResources = demoResources.map((res) => {
					// 		// 	if (res.id === data.resource_id) {
					// 		// 		res.access_policies = res.access_policies?.filter(
					// 		// 			(policy) => policy.identity_id !== data.identity_id
					// 		// 		);
					// 		// 	}
					// 		// 	return res;
					// 		// });
					// 		// demoResources = demoResources.filter((res) => res.id !== data.id);
				}
			}
		});
	});

	const newDemoResource = (): DemoResourceExtended => {
		return {
			id: 'new_' + Math.random().toString(36).substring(2, 9),
			name: '',
			description: '',
			access_right: Action.OWN,
			creation_date: new Date(Date.now())
		};
	};

	const addDemoResource = () => {
		socketio.addEntity(newDemoResource());
		// demoResources.unshift(newDemoResource());
	};

	// The backend is handling it, whether it's new or existing. If the id is a UUID, it tries to update an existing resource.
	const submitResource = (demoResource: DemoResourceExtended) => {
		socketio.submitEntity(demoResource);
		// if (demoResource.id?.slice(0, 4) === 'new_') {
		// 	editIds.delete(demoResource.id);
		// 	editIds = new Set(editIds); // trigger reactivity
		// }
		// socketio.client.emit('submit', { payload: demoResource });
	};

	// TBD: consider adding those directly to the onclick() event handler
	const deleteResource = (resourceId: string) => {
		socketio.deleteEntity(resourceId);
		// if (resourceId.slice(0, 4) === 'new_') {
		// 	// If the resource is new and has no id, we can just remove it from the local array
		// 	demoResources = demoResources.filter((res) => res.id !== resourceId);
		// } else {
		// 	socketio.client.emit('delete', resourceId);
		// }
		// if (editIds.has(resourceId)) {
		// 	editIds.delete(resourceId);
		// 	editIds = new Set(editIds); // trigger reactivity
		// }
	};

	const shareResource = (accessPolicy: AccessPolicy) => {
		socketio.shareEntity(accessPolicy);
		// if (debug) {
		// 	console.log(
		// 		'=== dashboard - backend-demo-resource - socketio - +page.svelte - share accessPolicy ==='
		// 	);
		// 	console.log(accessPolicy);
		// }
		// socketio.client.emit('share', accessPolicy);
	};

	const sortResourcesByCreationDate = (a: DemoResourceExtended, b: DemoResourceExtended) => {
		if (a.creation_date && b.creation_date) {
			const dateA = new Date(a.creation_date);
			const dateB = new Date(b.creation_date);
			return dateB.getTime() - dateA.getTime();
		} else {
			return 0;
		}
	};

	let ownedDemoResources: DemoResourceExtended[] = $derived(
		demoResources
			.filter((demoResource) => {
				if (demoResource.access_right === Action.OWN) {
					return demoResource;
				}
			})
			.sort(sortResourcesByCreationDate)
	);

	let writeDemoResources: DemoResourceExtended[] = $derived(
		demoResources
			.filter((demoResource) => {
				if (demoResource.access_right === Action.WRITE) {
					return demoResource;
				}
			})
			.sort(sortResourcesByCreationDate)
	);

	let readDemoResources: DemoResourceExtended[] = $derived(
		demoResources
			.filter((demoResource) => {
				if (demoResource.access_right === Action.READ) {
					return demoResource;
				}
			})
			.sort(sortResourcesByCreationDate)
	);

	onDestroy(() => socketio.client.disconnect());
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
				class="btn-neutral-container btn btn-gradient rounded-full"
				aria-label="Add Button"
				onclick={() => addDemoResource()}
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
			{#each editIds as id (id)}
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
					() => {
						if (demoResource.id) {
							return editIds.has(demoResource.id);
						} else {
							return false;
						}
					},
					(value) => {
						if (demoResource.id) {
							if (value) {
								editIds.add(demoResource.id);
							} else {
								editIds.delete(demoResource.id || '');
							}
							editIds = new Set(editIds);
						}
					}
				}
				identities={AccessHandler.reduceMicrosoftTeamsToIdentities(data.microsoftTeams)}
				{demoResource}
				{deleteResource}
				{submitResource}
				{shareResource}
			/>
			<!-- bind:demoResource={demoResources[idx]} -->
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
		<h3 class="title">
			<span class="icon-[fluent--people-team-16-filled]"></span>
			Teams access to demoresources: {data.microsoftTeams.length}
		</h3>
		<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="true">
			{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
				<div>
					<IdentityAccordion
						title={microsoftTeam.displayName || 'Unknown Team'}
						id={microsoftTeam.id || Math.random().toString(36).substring(2, 9)}
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
							<JsonData data={microsoftTeam} />
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
			<DemoResourceContainer {demoResource} {submitResource} />
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
		<h3 class="title">
			<span class="icon-[tabler--eye] bg-neutral"></span>
			Demo Resources with read access: {readDemoResources.length}
		</h3>
		{#each readDemoResources as demoResource, idx (demoResource.id)}
			<DemoResourceContainer {demoResource} />
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
</div>

<!-- <ul
    class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden min-w-[15rem] shadow-xs"
    role="menu"
    aria-orientation="vertical"
    aria-labelledby="action-share"
>
    <form
        method="POST"
        name="actionButtonShareForm"
        use:enhance={async () => {
            actionButtonShareMenu?.close();
            return async ({ result, update }) => {
                handleRightsChangeResponse(result, update);
            };
        }}
    >
        {#each teams as team, i (i)}
            <ShareItem
                resourceId="actionButtonShareResourceId"
                icon="icon-[fluent--people-team-16-filled]"
                identity={team}
            />
        {/each}
    </form>
    <li class="dropdown-footer gap-2">
        <button
            class="btn dropdown-item btn-text text-secondary content-center justify-start"
            >... more options</button
        >
    </li>
</ul> -->
