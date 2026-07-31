<script lang="ts">
	import Title from '$components/Title.svelte';

	import Toolbar from './Toolbar.svelte';
</script>

<Title id="drawer-skeleton">Drawer skeleton</Title>
<Toolbar id="skeleton" />

<Title id="drawer-with-title">Drawer with title</Title>
<Toolbar id="with-title" title="Custom Drawer Title" />

<Title id="drawer-with-body">Drawer with body</Title>
<Toolbar id="with-body" title="Drawer with Body">
	<p>Some text as placeholder. There can be elements like, text, images, lists, etc.</p>
	<div
		class="bg-base-150 shadow-outline max-h-96 min-h-44 overflow-y-auto rounded-lg p-2 shadow-inner"
	>
		Some text
	</div>
</Toolbar>

{#snippet closeButton()}
	<button
		type="button"
		class="btn btn-secondary-container btn-gradient shadow-outline"
		data-overlay="#overlay-with-footer">Close</button
	>
{/snippet}

<Title id="drawer-with-footer">Drawer with footer</Title>
<Toolbar id="with-footer" title="Drawer with Footer" footer={closeButton} />
