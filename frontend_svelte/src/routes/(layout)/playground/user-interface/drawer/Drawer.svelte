<script lang="ts">
	import type { Snippet } from 'svelte';

	import { initOverlay } from '$lib/userInterface';
	let {
		id,
		title,
		children,
		footer
	}: { id: string; title?: string; children?: Snippet; footer?: Snippet } = $props();
</script>

<button
	type="button"
	class="btn btn-primary btn-gradient shadow-outline"
	aria-haspopup="dialog"
	aria-expanded="false"
	aria-controls={'overlay-' + id}
	data-overlay={'#overlay-' + id}>{title ?? 'Open drawer'}</button
>
<div
	id={'overlay-' + id}
	class="overlay drawer drawer-end bg-base-200 overlay-open:translate-x-0 hidden"
	role="dialog"
	tabindex="-1"
	{@attach initOverlay}
>
	<div class="drawer-header">
		<h3 class="drawer-title">{title}</h3>
		<button
			type="button"
			class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
			aria-label="Close"
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
