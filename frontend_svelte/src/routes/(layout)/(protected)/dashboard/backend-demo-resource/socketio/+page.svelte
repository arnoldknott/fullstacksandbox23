<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import { SocketIO, type SocketioConnection } from '$lib/socketio';
	import { page } from '$app/state';
	import type { DemoResource } from '$lib/types';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';
	import IdentityAccordion from '../../identities/IdentityAccordion.svelte';
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

	let demoResources: DemoResource[] = $state([]);
	$effect(() => {
		socketio.client.on('transfer', (data: DemoResource) => {
			// if (debug) {
			// console.log(
			// 	'=== dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
			// );
			// console.log(data);
			// }
			demoResources.push(data);
		});
	});
</script>

<div class="mb-2 flex items-center gap-1">
	<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
	<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
</div>

<div class="mb-5">
	<button class="btn-neutral-container btn" aria-label="Add Button">
		<span class="icon-[fa6-solid--plus]"></span> Add
	</button>
</div>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-2" id="demoResourcesContainer">
	<div>
		{#each demoResources as demoResource (demoResource.id)}
			<div class="bg-base-300 shadow-shadow m-2 flex flex-col rounded-xl p-2 shadow-xl">
				<h5 class="title-large">{demoResource.name}</h5>
				<div class="flex flex-row">
					<div class="grow">
						<p>{demoResource.description}</p>
					</div>
					<div class="join flex flex-row items-end justify-center">
						<button
							class="btn btn-secondary-container text-secondary-container-content btn-sm join-item grow"
							aria-label="Edit Button"
						>
							<!-- onclick={() => (edit ? (edit = false) : (edit = true))} -->
							<span class="icon-[material-symbols--edit-outline-rounded]"></span>
						</button>
						<div class="dropdown join-item relative inline-flex grow [--placement:top]">
							<!-- bind:this={actionButtonShareMenuElement} -->
							<button
								id="action-share"
								class="dropdown-toggle btn btn-secondary-container text-secondary-container-content btn-sm w-full rounded-none"
								aria-haspopup="menu"
								aria-expanded="false"
								aria-label="Share with"
							>
								<span class="icon-[tabler--share-2]"></span>
								<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-4"></span>
							</button>
						</div>
						<button
							class="btn btn-error-container bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content btn-sm join-item grow border-0"
							aria-label="Delete Button"
							name="id"
							formaction="?/delete"
						>
							<span class="icon-[tabler--trash]"></span>
						</button>
					</div>
				</div>
			</div>
			<div class={debug ? 'block' : 'hidden'}>
				<p class="title">🚧 Debug Information 🚧</p>
				<JsonData data={demoResource} />
			</div>
			<div class="divider-outline-variant divider"></div>
		{/each}
	</div>
	<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="true">
		{#each data.microsoftTeams as microsoftTeam (microsoftTeam.id)}
			<div>
				<IdentityAccordion title={microsoftTeam.displayName} id={microsoftTeam.id}>
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
