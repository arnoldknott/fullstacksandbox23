<script lang="ts">
	import type { DemoResourceExtended } from '$lib/types';
	import { Action } from '$lib/accessHandler';
	let {
		demoResource,
		edit = false,
		deleteResource = (_id: string) => {},
		submitResource = (_resource: DemoResourceExtended) => {}
	}: {
		demoResource: DemoResourceExtended;
		edit?: boolean;
		deleteResource?: (id: string) => void;
		submitResource?: (resource: DemoResourceExtended) => void;
	} = $props();
	let formatedDate = $derived(
		demoResource.creation_date
			? new Date(demoResource.creation_date).toLocaleString('da-DK', { timeZone: 'CET' })
			: new Date(Date.now()).toLocaleString('da-DK', { timeZone: 'CET' })
	);
	if (demoResource.id?.slice(0, 4) === 'new_') edit = true;
	// TBD: trigger submitResource when edit changes to false
</script>

<div class="bg-base-300 shadow-shadow m-2 flex flex-col rounded-xl p-2 shadow-xl">
	<div class="flex flex-row justify-between">
		<h5
			contenteditable={edit}
			class="title justify-self-start"
			onblur={(event) => {
				// TBD: onblur changes edit to false, as DemoResourceContainer is getting reloaded
				demoResource.name = (event.target as HTMLElement)?.innerText || '';
				submitResource(demoResource);
			}}
		>
			{demoResource.name}
		</h5>
		<div class="label justify-self-end">
			{formatedDate}
		</div>
	</div>
	<div class="flex flex-row">
		<div class="body-small grow">
			<p
				contenteditable={edit}
				onblur={(event) => {
					demoResource.description = (event.target as HTMLElement)?.innerText || '';
					submitResource(demoResource);
				}}
			>
				{demoResource.description}
			</p>
			<div class="badge badge-xs label-small">{demoResource.id?.slice(0, 7)}</div>
		</div>
		{#if demoResource.user_right === Action.Write || demoResource.user_right === Action.Own}
			<div class="join flex flex-row items-end justify-center">
				<button
					class="btn btn-secondary-container text-secondary-container-content btn-sm join-item grow"
					aria-label="Edit Button"
					onclick={() => (edit = !edit)}
				>
					<span class="icon-[material-symbols--edit-outline-rounded] {!edit || 'hidden'}"></span>
					<span class="grid place-items-center {edit || 'hidden'}">
						<span
							class="icon-[material-symbols--edit-outline-rounded] col-start-1 row-start-1 size-3"
						></span>
						<span class="icon-[ic--outline-do-not-disturb] col-start-1 row-start-1 size-4"></span>
					</span>
				</button>
				{#if demoResource.user_right === Action.Own}
					<div class="dropdown join-item relative inline-flex grow [--placement:top]">
						<!-- bind:this={actionButtonShareMenuElement} -->
						<button
							id="action-share"
							class="dropdown-toggle btn btn-secondary-container text-secondary-container-content btn-sm w-full rounded-none"
							aria-haspopup="menu"
							aria-expanded="false"
							aria-label="Share with"
						>
							<span class="icon-[tabler--share-2]"></span>
							<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-4"></span>
						</button>
					</div>
					<button
						class="btn btn-error-container bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content btn-sm join-item grow border-0"
						aria-label="Delete Button"
						name="id"
						onclick={() => !demoResource.id || deleteResource(demoResource.id)}
					>
						<span class="icon-[tabler--trash]"></span>
					</button>
				{/if}
			</div>
		{/if}
	</div>
</div>
