<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import type { PageProps } from './$types';
    import { enhance  } from '$app/forms';
    import { page } from '$app/state';

	let { data }: PageProps = $props();

	console.log('=== playground - dataflow - +page.svelte ===');
    const dataWithoutBackEndConfiguration = Object.fromEntries(
        Object.entries(data).filter(([key]) => !key.startsWith('backendAPIConfiguration'))
    );
	console.log(dataWithoutBackEndConfiguration); // { layoutServerTs: 1, layout.ts: 2, pageServerTs: 3, pageTs: 4  }
</script>

<div class="col-start-2 col-end-5">
	<p class="title">+page.svelte</p>
	<JsonData data={dataWithoutBackEndConfiguration} />
</div>

<!-- When using named actions, the default action cannot be used. -->
<!-- <form method="post">
    <p class="title">Default HTML only</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled grow">
            <label class="input-filled-label" for="inputDefault">Default action</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputDefault" name="inputDefault" />
        </div>
        <button class="btn">Send</button>
    </div>
</form> -->

<form method="post" action="?/named">
    <p class="title">Named HTML only</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-secondary grow">
        <label class="input-filled-label" for="inputNamed">Named action</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputNamed" name="inputNamed" />
        </div>
        <button class="btn btn-secondary">Send</button>
    </div>
</form>

<form method="post" action="?/enhanced" use:enhance>
    <p class="title">Use:enhance (default)</p>
    <div class="flex flex-row items-end gap-2">
        <div class="input-filled input-accent grow">
        <label class="input-filled-label" for="inputEnhanced">Enhanced action</label>
            <input class="input input-sm" placeholder="send data to server" type="text" id="inputEnhanced" name="inputEnhanced" />
        </div>
        <button class="btn btn-accent">Send</button>
    </div>
</form>

<div class="col-span-full">
    <p class="title">Form result</p>
    <JsonData data={page.form} />
</div>

