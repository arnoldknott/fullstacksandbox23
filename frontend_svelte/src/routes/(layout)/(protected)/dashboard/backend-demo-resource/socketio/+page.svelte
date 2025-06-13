<script lang="ts">
    import JsonData from "$components/JsonData.svelte";
    import { SocketIO, type SocketioConnection } from "$lib/socketio";
    import {page} from "$app/state";
	import type { DemoResource } from "$lib/types";
    let debug = $state(false)

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


{#each demoResources as demoResource }
    <JsonData data={demoResource} />
{/each}