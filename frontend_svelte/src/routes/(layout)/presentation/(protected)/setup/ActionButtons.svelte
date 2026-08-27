<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import type { SocketIO } from '$lib/socketio.svelte';
	import { initDropdown } from '$lib/userInterface';

	import ShareItem from '../../../playground/components/ShareItem.svelte';

	let {
		resourceId,
		accessRight,
		socketio,
		actions = [Action.OWN, Action.WRITE, Action.READ, undefined]
	}: {
		resourceId: string;
		accessRight: Action | undefined;
		socketio: SocketIO;
		actions?: (Action | undefined)[];
	} = $props();

	let actionButtonShareMenu: HTMLElement | null = $state(null);
</script>

<div class="join inline-flex flex-row">
	<!-- <a
			href={resolve('/(layout)/presentation/(protected)/setup/[id]', {
				id: path || resourceId
			})}
			aria-label={`Setup presentation ${path || resourceId}`}
			class=""
		> -->
	<!-- TBD: hide the buttons, where the access_right for the logged in user are not enough to execute the action -->
	{#if accessRight === Action.OWN || accessRight === Action.WRITE}
		<button
			class="btn btn-secondary-container btn-gradient btn-sm text-secondary-container-content join-item shadow-outline {accessRight ===
			Action.OWN
				? 'rounded-l-full'
				: 'rounded-full'} shadow-sm"
			aria-label="Edit Button"
			// TBD: pass setup page as a parameter to the component, so that it can be used here
			onclick={() =>
				goto(resolve('/(layout)/presentation/(protected)/setup/[id]', { id: resourceId }))}
		>
			<span class="icon-[tabler--settings] size-4"></span>
			<!-- <span
					class="hidden 2xl:block">Edit</span
				> -->
		</button>

		<!-- </a> -->
		{#if accessRight === Action.OWN}
			<div
				class="dropdown join-item relative inline-flex [--auto-close:inside] [--placement:top]"
				bind:this={actionButtonShareMenu}
				{@attach initDropdown}
			>
				<button
					id="action-share"
					class="dropdown-toggle btn btn-secondary-container btn-gradient btn-sm text-secondary-container-content shadow-outline w-full rounded-none shadow-sm"
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
					{#each AccessHandler.createShareOptions(socketio.identities, socketio.accessPolicies[resourceId]) as shareOption, i (i)}
						<ShareItem
							{resourceId}
							{shareOption}
							{socketio}
							{actions}
							closeShareMenu={() => window.HSDropdown.close(actionButtonShareMenu)}
						/>
					{/each}
					<!-- <li class="dropdown-footer gap-2">
								<button
									class="btn dropdown-item btn-text text-secondary content-center justify-start"
									>... more options</button
								>
							</li> -->
				</ul>
			</div>
			<button
				class="btn btn-error-container btn-gradient btn-sm bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content join-item shadow-outline rounded-r-full border-0 shadow-sm"
				aria-label="Delete Button"
				name="id"
				onclick={() => !resourceId || socketio.deleteEntity(resourceId)}
			>
				<span class="icon-[tabler--trash] size-4"></span>
				<!-- <span class="hidden 2xl:block">Delete</span> -->
			</button>
		{/if}
	{/if}
</div>
