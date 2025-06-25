<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import { SocketIO, type SocketioConnection } from '$lib/socketio';
	import { page } from '$app/state';
	import type { DemoResourceExtended } from '$lib/types';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';
	import IdentityAccordion from '../../identities/IdentityAccordion.svelte';
	import { Action } from '$lib/accessHandler';
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

	const connection: SocketioConnection = {
		namespace: '/demo-resource',
		cookie_session_id: page.data.session.sessionId,
		requestAccessData: true
	};

	const socketio = new SocketIO(connection);

	let demoResources: DemoResourceExtended[] = $state([]);
	$effect(() => {
		socketio.client.on('transfer', (data: DemoResourceExtended) => {
			// if (debug) {
			// 	console.log(
			// 		'=== dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
			// 	);
			// 	console.log(data);
			// }
			demoResources.push(data);
		});
		socketio.client.on('deleted', (resource_id: string) => {
			if (debug) {
				console.log(
					'=== dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
				);
				console.log(resource_id);
			}
			demoResources = demoResources.filter((res) => res.id !== resource_id);
		});
	});

    const addDemoResource = () => {
        const newResource: DemoResourceExtended =
        {
            id: 'new_' + Math.random().toString(36).substring(2, 9),
            name: "",
            user_right: Action.Own,
			creation_date: new Date(Date.now()),
        };
        demoResources.push(newResource);
    };

    const deleteResource = (resourceId: string) => { socketio.client.emit('delete', resourceId) };

    const submitResource = (demoResource: DemoResourceExtended) => {
        if (demoResource.id?.slice(0, 4) === 'new_') {
            // If the resource is new, we need to emit a create event, remove the id and the backend will create a new resource
            const { id, ...rest } = demoResource;
            socketio.client.emit('submit', rest);
        } else {
            // Otherwise, we can update the existing resource
            socketio.client.emit('submit', demoResource);
        }
    };

	let ownedDemoResources: DemoResourceExtended[] = $derived(
		demoResources
			.filter((demoResource) => {
				if (demoResource.user_right === Action.Own) {
					return demoResource;
				}
			})
			.sort((a, b) => {
				if (a.creation_date && b.creation_date) {
					const dateA = new Date(a.creation_date);
					const dateB = new Date(b.creation_date);
					return dateB.getTime() - dateA.getTime();
				} else {
					return 0;
				}
			})
	);
	let writeDemoResources: DemoResourceExtended[] = $derived(
		demoResources.filter((demoResource) => {
			if (demoResource.user_right === Action.Write) {
				return demoResource;
			}
		})
	);
	let readDemoResources: DemoResourceExtended[] = $derived(
		demoResources.filter((demoResource) => {
			if (demoResource.user_right === Action.Read) {
				return demoResource;
			}
		})
	);
</script>

<div class="mb-2 flex items-center gap-1">
	<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
	<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
</div>

<div class="mb-5">
	<button class="btn-neutral-container btn" aria-label="Add Button" onclick={() => addDemoResource()}>
		<span class="icon-[fa6-solid--plus]"></span> Add
	</button>
    <!-- <JsonData data={array} /> -->
</div>


<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-2" id="demoResourcesContainer">
	<div>
		<h3 class="title">Demo Resources with owner access</h3>
		{#each ownedDemoResources as demoResource, idx (demoResource.id)}
            <DemoResourceContainer {demoResource} {deleteResource} {submitResource} />
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
		<h3 class="title">Teams access to demoresources</h3>
		<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="true">
			{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
				<div>
					<IdentityAccordion title={microsoftTeam.displayName} id={microsoftTeam.id} open={false}>
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
		<h3 class="title">Demo Resources with write access</h3>
        {#each writeDemoResources as demoResource (demoResource.id)}
            <DemoResourceContainer {demoResource} {submitResource}/>
		{/each}
	</div>
	<div>
		<h3 class="title">Demo Resources with read access</h3>
		{#each readDemoResources as demoResource (demoResource.id)}
			<DemoResourceContainer {demoResource}/>
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
