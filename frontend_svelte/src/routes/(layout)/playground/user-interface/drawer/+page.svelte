<script lang="ts">
	import Title from '$components/Title.svelte';

	import Drawer from './Drawer.svelte';
</script>

<Title id="drawer-skeleton">Drawer skeleton</Title>
<Drawer id="skeleton" />

<Title id="drawer-with-title">Drawer with title</Title>
<Drawer id="with-title" title="Custom Drawer Title" />

<Title id="drawer-with-body">Drawer with body</Title>
<Drawer id="with-body" title="Drawer with Body">
	<p>Some text as placeholder. There can be elements like, text, images, lists, etc.</p>
	<div
		class="bg-base-150 shadow-outline max-h-96 min-h-44 overflow-y-auto rounded-lg p-2 shadow-inner"
	>
		Some text
	</div>
</Drawer>

{#snippet closeButton()}
	<button
		type="button"
		class="btn btn-secondary-container btn-gradient shadow-outline"
		data-overlay="#overlay-with-footer"
	>
		Close
	</button>
{/snippet}

<Title id="drawer-with-footer">Drawer with footer</Title>
<Drawer id="with-footer" title="Drawer with Footer" footer={closeButton} />
