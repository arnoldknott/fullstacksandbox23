<script lang="ts">
    import JsonData from "$components/JsonData.svelte";
    import { SocketIO, type SocketioConnection } from "$lib/socketio";
    import {page} from "$app/state";
	import type { DemoResource } from "$lib/types";
	import { goto } from "$app/navigation";
	import Heading from "$components/Heading.svelte";
    let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false)

    $effect(() => {
        if (debug) {
            goto(`?debug=true`, { replaceState: true });
        } else {
            goto(`?`, { replaceState: true });
        }
    })


    const connection: SocketioConnection = {
        namespace: "/demo-resource",
        room: "",// use in hierarchical resource system for parent resource id and/or identity (group) id?
        cookie_session_id: page.data.session.sessionId
    };

    const socketio = new SocketIO(connection);

    let demoResources: DemoResource[] = $state([])
    $effect(() => {
        socketio.client.on("transfer", (data: DemoResource) => {
            // if (debug) {
            console.log("=== dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ===");
            console.log(data);
            // }
            demoResources.push(data);
        });
    })
</script>

<div class="mb-2 flex items-center gap-1">
	<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
	<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
</div>

<div class="mb-5">
    <button
        class="btn-neutral-container btn"
        aria-label="Add Button"
    >
        <span class="icon-[fa6-solid--plus]"></span> Add
    </button>
</div>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-2" id="demoResourcesContainer">
    {#each demoResources as demoResource (demoResource.id) }
        <div>
            <div class="flex flex-row">
                <div class="grow">
                    <h5 class="title-large">{demoResource.name}</h5>
                    <p>{demoResource.description}</p>
                </div>
                <div class="join flex flex-row items-center justify-center">
					<button
						class="btn btn-secondary-container text-secondary-container-content join-item grow"
						aria-label="Edit Button"
					>
                    <!-- onclick={() => (edit ? (edit = false) : (edit = true))} -->
						<span class="icon-[material-symbols--edit-outline-rounded]"></span>
					</button>
					<div
						class="dropdown join-item relative inline-flex grow [--placement:top]"
					>
                    <!-- bind:this={actionButtonShareMenuElement} -->
						<button
							id="action-share"
							class="dropdown-toggle btn btn-secondary-container text-secondary-container-content w-full rounded-none"
							aria-haspopup="menu"
							aria-expanded="false"
							aria-label="Share with"
						>
							<span class="icon-[tabler--share-2]"></span>
							<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-4"></span>
						</button>
					</div>
					<button
						class="btn btn-error-container bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content join-item grow border-0"
						aria-label="Delete Button"
						name="id"
						formaction="?/delete"
					>
						<span class="icon-[tabler--trash]"></span>
					</button>
				</div>
            </div>
            <div class="divider-outline-variant divider"></div>
        </div>
        <div class={debug ? 'block' : 'hidden'}>
            <JsonData data={demoResource} />
        </div>
    {/each}
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