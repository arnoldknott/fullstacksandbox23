<script lang="ts">
	import type { PageData } from './$types';
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	import '@material/web/dialog/dialog.js';
	import type { Dialog } from '@material/web/dialog/internal/dialog';
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	import '@material/web/button/filled-tonal-button.js';
	import '@material/web/select/filled-select.js';
	import '@material/web/select/select-option.js';
	import '@material/web/list/list.js';
	import '@material/web/list/list-item.js';
	let { data }: { data: PageData } = $props();
	const demo_resources = data.demoResources;

	let demo_resource_dialog: Dialog;
	// let name = $state('');
	// let description = $state('');
	// let language = $state('en-US');
	const cancelForm = (event: Event) => {
		event.preventDefault();
		demo_resource_dialog.close();
	};
</script>

<!-- <code><pre>{JSON.stringify(demo_resources, null, ' ')}</pre></code> -->

{#each demo_resources as demo_resource}
	<Title>{demo_resource.name}</Title>
	<JsonData data={demo_resource} />
{/each}

<!-- Form not available without JavaScript. -->

<md-filled-button
	onclick={() => demo_resource_dialog.show()}
	role="button"
	tabindex="0"
	onkeydown={(event: KeyboardEvent) => event.key === 'Enter' && demo_resource_dialog.show()}
	>New</md-filled-button
>

<md-dialog id="demo_resource_dialog" bind:this={demo_resource_dialog} class="w-fill">
	<div slot="headline" class="w-64">Demo Resource</div>
	<form slot="content" id="post-demo-resource" method="POST" class="flex flex-col">
		<md-filled-text-field label="Name" name="name" class="w-full"> </md-filled-text-field>
		<br />
		<md-filled-text-field
			label="Description"
			name="description"
			type="textarea"
			rows="3"
			class="my-3 w-full"
		>
		</md-filled-text-field>
		<md-filled-select label="Language" name="language" class="w-full">
			<md-select-option value="en-US">
				<div slot="headline">en-US</div>
			</md-select-option>
			<md-select-option value="dk-DK">
				<div slot="headline">dk-DK</div>
			</md-select-option>
			<md-select-option value="de-DE">
				<div slot="headline">de-DE</div>
			</md-select-option>
		</md-filled-select>
		<!-- <button>Submit</button> -->
		<!-- <md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button> -->
		<div slot="actions" class="ml-auto py-4">
			<md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button>
			<md-filled-tonal-button
				role="button"
				tabindex="0"
				onclick={(event: Event) => cancelForm(event)}
				onkeydown={(event: KeyboardEvent) => event.key === 'Enter' && cancelForm(event)}
				>Cancel</md-filled-tonal-button
			>
		</div>
	</form>
</md-dialog>

<style>
	/* Works - overriding local variables, but ugly! */
	/* #demo_resource_dialog {
		--md-dialog-headline-color: #e4a112;
		--md-dialog-container-color: #e5deb9;
	} */
	#post-demo-resource {
		display: flex;
		flex-direction: column;
	}
	#post-demo-resource md-filled-text-field {
		margin-bottom: 1rem;
	}
	#post-demo-resource md-filled-select {
		margin-bottom: 1rem;
	}
	#post-demo-resource md-filled-button {
		margin-top: 1rem;
	}
	#post-demo-resource md-filled-tonal-button {
		margin-top: 1rem;
	}
</style>
