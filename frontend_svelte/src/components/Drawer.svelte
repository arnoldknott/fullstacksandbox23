<script lang="ts">
	import type { Snippet } from 'svelte';

	import { initOverlay } from '$lib/userInterface';
	let {
		id,
		title,
		children,
		footer,
		activationElement
	}: {
		id: string;
		title?: string;
		children?: Snippet;
		footer?: Snippet;
		activationElement?: Snippet;
	} = $props();
</script>

{#if activationElement}
	{@render activationElement?.()}
{:else}
	<button
		type="button"
		class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
		aria-label="Open drawer"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls={'overlay-' + id}
		data-overlay={'#overlay-' + id}
	>
		{title ?? 'Open tools'}
	</button>
{/if}
<div
	id={'overlay-' + id}
	class="overlay drawer drawer-end bg-base-200 overlay-open:translate-x-0 hidden"
	role="dialog"
	tabindex="-1"
	{@attach initOverlay}
>
	<div class="drawer-header">
		<h3 class="drawer-title" id={'title-' + id}>{title}</h3>
		<button
			type="button"
			class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
			aria-label="Close drawer"
			data-overlay={'#overlay-' + id}
		>
			<span class="icon-[tabler--x] size-5"></span>
		</button>
	</div>
	<div class="drawer-body">
		{@render children?.()}
	</div>
	<div class="drawer-footer">
		{@render footer?.()}
	</div>
</div>
