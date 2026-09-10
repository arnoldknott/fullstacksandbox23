<script lang="ts">
	import type { SocketIO } from '$lib/socketio.svelte';
	import { initDropdown } from '$lib/userInterface';

	let { socketio }: { socketio: SocketIO } = $props();
	let actionButtonMenu: HTMLElement | null = $state(null);
</script>

<div class="join inline-flex flex-row">
	<div
		class="dropdown join-item relative inline-flex [--auto-close:inside] [--placement:top]"
		bind:this={actionButtonMenu}
		{@attach initDropdown}
	>
		<button
			id="action-share"
			class="dropdown-toggle btn btn-secondary-container btn-gradient btn-sm text-secondary-container-content shadow-outline w-full rounded-l-full shadow-sm"
			aria-haspopup="menu"
			aria-expanded="false"
			aria-label="Share with"
		>
			<span class="icon-[tabler--share-2] size-4"></span>
			<!-- <span class="hidden 2xl:block"
					>Share</span
				> -->
			<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-3"></span>
		</button>
		<ul
			class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden min-w-[15rem] shadow-xs"
			role="menu"
			aria-orientation="vertical"
			aria-labelledby="action-share"
		>
			<li>ShareOption 1</li>
			<li>ShareOption 2</li>
			<li>ShareOption 3</li>
		</ul>
	</div>
	<button
		class="btn btn-error-container btn-gradient btn-sm bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content join-item shadow-outline rounded-r-full border-0 shadow-sm"
		aria-label="Delete Button"
		name="id"
		onclick={() =>
			// TBD: should it exclude the ones, where the user does not have owner rights, or just let the bakend reject the deletion?
			socketio.selections?.['selected'].forEach((entityId) => socketio.deleteEntity(entityId))}
	>
		<span class="icon-[tabler--trash] size-4"></span>
	</button>
</div>
