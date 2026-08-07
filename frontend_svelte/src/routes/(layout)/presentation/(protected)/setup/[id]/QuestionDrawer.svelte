<script lang="ts">
	import Drawer from '$components/Drawer.svelte';

	let mode: 'copy' | 'link' = $state('copy');
</script>

{#snippet openButtons()}
	<button
		type="button"
		class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
		aria-label="Open drawer"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="overlay-drawer-questions"
		data-overlay="#overlay-drawer-questions"
		onclick={() => (mode = 'copy')}
	>
		<span class="icon-[tabler--copy] size-4"></span>
		Copy Existing Questions
	</button>
	<button
		type="button"
		class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
		aria-label="Open drawer"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="overlay-drawer-questions"
		data-overlay="#overlay-drawer-questions"
		onclick={() => (mode = 'link')}
	>
		<span class="icon-[tabler--link] size-4"></span>
		Link Existing Questions
	</button>
{/snippet}

<Drawer
	id="drawer-questions"
	icon={mode === 'copy' ? 'icon-[tabler--copy]' : 'icon-[tabler--link]'}
	title={mode.charAt(0).toUpperCase() + mode.slice(1) + ' Existing Questions'}
	activationElement={openButtons}
>
	<button
		type="button"
		class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
		aria-label="Switch mode"
		onclick={() => (mode = mode === 'copy' ? 'link' : 'copy')}
	>
		<span class="{mode === 'copy' ? 'icon-[tabler--link]' : 'icon-[tabler--copy]'} size-4"></span>
		{mode === 'copy' ? 'Link ' : 'Copy'} Existing Questions
	</button>
	<p class="title">Drawer to select existing questions</p>
	{#if mode === 'copy'}
		<p>Mode: Copy - don't keep the original answers and don't keep in sync</p>
	{:else if mode === 'link'}
		<p>Mode: Link - keeps answers in sync</p>
	{/if}
</Drawer>
