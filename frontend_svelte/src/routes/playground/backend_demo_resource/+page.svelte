<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	import '@material/web/dialog/dialog.js';
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	import '@material/web/button/filled-tonal-button.js';
	let { data }: { data: PageData } = $props();
	let title = $state('');
	const demo_resources = data.demoResources;
	let demo_resource_dialog: HTMLDialogElement;
</script>

<!-- <code><pre>{JSON.stringify(demo_resources, null, ' ')}</pre></code> -->

{#each demo_resources as demo_resource}
	<Title>{demo_resource.name}</Title>
	<JsonData data={demo_resource} />
{/each}


<md-filled-button onclick={async () => await demo_resource_dialog.show()} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && demo_resource_dialog.show()}>New</md-filled-button>

<md-dialog id="demo_resource_dialog" bind:this={demo_resource_dialog} open>
	<div slot="headline">
		Demo Resource
	</div>
	<form slot="content" id="post-demo-resource" method="POST">
		<md-filled-text-field label="Title" value={title}>
		</md-filled-text-field>
	</form>
	<div slot="actions">
		<md-filled-button role="button" tabindex="0">OK</md-filled-button>
		<md-filled-tonal-button role="button" tabindex="0" onclick={async () => await demo_resource_dialog.close()} onkeydown={(e) => e.key === 'Enter' && demo_resource_dialog.close()}>Cancel</md-filled-tonal-button>
	</div>
</md-dialog>
