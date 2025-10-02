<script lang="ts">
	import { Action, AccessHandler } from '$lib/accessHandler';
	import type { AccessPolicy, AccessShareOption } from '$lib/types';
	import { enhance } from '$app/forms';
	import type { ActionResult } from '@sveltejs/kit';

	let {
		resourceId,
		shareOption,
		share,
		closeShareMenu
		// handleRightsChangeResponse
	}: {
		resourceId: string;
		shareOption: AccessShareOption;
		share?: (accessPolicy: AccessPolicy) => void;
		// handleRightsChangeResponse?: (result: ActionResult, update: () => void) => void;
		closeShareMenu?: () => void;
	} = $props();

	// let selectedAction = $state(shareOption.action);
	// let selectionFocused = $state(false);

	// let browser = $derived.by(() => {
	// 	if (typeof navigator !== 'undefined') {
	// 		const userAgent = navigator.userAgent;
	// 		if (userAgent.includes('Chrome')) {
	// 			return 'Chrome';
	// 		} else if (userAgent.includes('Firefox')) {
	// 			return 'Firefox';
	// 		} else if (userAgent.includes('Safari')) {
	// 			return 'Safari';
	// 		} else if (userAgent.includes('Edge')) {
	// 			return 'Edge';
	// 		} else {
	// 			return 'Other';
	// 		}
	// 	}
	// 	return 'Unknown';
	// });

	// TBD: consider moving to AccessHandler
	const desiredActions = (selectedAction?: Action) => {
		let action = shareOption.action;
		let newAction = undefined;
		// deleting access policy:
		if (selectedAction === undefined && action) {
			action = undefined;
			newAction = undefined;
		}
		// creating a new access policy:
		else if (shareOption.action === undefined) {
			action = selectedAction;
		}
		// updating an existing access policy:
		// else if (selectedAction && shareOption.action !== selectedAction) {
		else {
			newAction = selectedAction;
		}
		// console.log(
		// 	'=== shareItem - desiredActions - Values for access policy ===',
		// 	shareOption.action,
		// 	selectedAction
		// );
		return {
			action: action,
			new_action: newAction
		};
	};
</script>

{#snippet shareButton(selectedAction?: Action)}
	<li>
		<button
			data-sveltekit-preload-data={false}
			class="btn dropdown-item dropdown-close btn-text max-w-40 content-center"
			name="id"
			type="submit"
			value={resourceId}
			formaction={!share
				? `?/share&identity-id=${shareOption.identity_id}&action=${desiredActions(selectedAction).action}&new-action=${desiredActions(selectedAction).new_action}`
				: undefined}
			onclick={() => {
				if (share) {
					share({
						resource_id: resourceId,
						identity_id: shareOption.identity_id,
						action: desiredActions(selectedAction).action,
						new_action: desiredActions(selectedAction).new_action
					});
					if (closeShareMenu) {
						closeShareMenu();
					}
				}
			}}
			aria-label={String(selectedAction) || 'remove'}
		>
			<span class={AccessHandler.rightsIcon(selectedAction)}></span>
		</button>
	</li>
{/snippet}

<!-- {#snippet shareSelectOptionIcon(right: Action | undefined)}
	<span class={AccessHandler.rightsIcon(right)}></span>
{/snippet}

{#snippet shareSelectOption(right: Action | undefined)}
	{#if browser === 'Firefox' || browser === 'Safari'}
		<option
			class="dropdown-item dropdown-close bg-base-300 text-{AccessHandler.rightsIconColor(
				right
			)} custom-option-own border-none"
			value={right}
		>
			{AccessHandler.rightsIconEmoji(right)}&nbsp;{right || 'none'}
		</option>
	{:else}
		<option
			class="dropdown-item dropdown-close bg-base-300 text-{AccessHandler.rightsIconColor(
				right
			)} custom-option-own border-none"
			value={right}
		>
			{@render shareSelectOptionIcon(right)}
			{right || 'none'}
		</option>
	{/if}
{/snippet} -->

<li>
	<div class="tooltip relative flex items-center [--placement:top]">
		<div
			class="dropdown-item text-secondary tooltip-toggle w-full max-w-42 content-center"
			aria-label={shareOption.identity_name}
		>
			<span class="{AccessHandler.identityIcon(shareOption.identity_type)} shrink-0"></span>
			{shareOption.identity_name.slice(0, 12)}{shareOption.identity_name.length > 13
				? ' ...'
				: null}
			{#if shareOption.identity_name.length > 12}
				<span
					class="tooltip-content tooltip-shown:visible tooltip-shown:opacity-100 bg-base-300 rounded-xl outline"
					role="tooltip"
				>
					{shareOption.identity_name}
				</span>
			{/if}
		</div>
		<div class="mr-2">
			<span class="{AccessHandler.rightsIcon(shareOption.action)} ml-2 size-4"></span>
		</div>
		<div class="dropdown relative inline-flex [--offset:0] [--placement:left-start]">
			<button
				id="rights-{shareOption.identity_id}"
				type="button"
				class="dropdown-toggle btn btn-text bg-base-300"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="Dropdown"
			>
				<span class="icon-[tabler--chevron-down] dropdown-open:rotate-180 size-4"></span>
			</button>
			<ul
				class="dropdown-menu outline-outline bg-base-300 dropdown-open:opacity-100 hidden outline-2"
				role="menu"
				aria-orientation="vertical"
				aria-labelledby="rights-{shareOption.identity_id}"
			>
				{@render shareButton(Action.OWN)}
				{@render shareButton(Action.WRITE)}
				{@render shareButton(Action.READ)}
				{@render shareButton()}
			</ul>
		</div>
		<!-- <div class="relative flex flex-row">
			<form
				class="w-fit"
				method="POST"
				name="selection-right-form"
				action={`?/share&identity-id=${shareOption.identity_id}&action=${desiredActions(selectedAction).action}&new-action=${desiredActions(selectedAction).new_action}`}
				use:enhance={async ({ formData }) => {
					formData.append('id', 'selection-resource-id');
					return async ({ result, update }) => {
						handleRightsChangeResponse?.(result, update);
					};
				}}
			>
				<select
					class="select custom-select bg-base-300 w-full {AccessHandler.rightsIcon(
						shareOption.action
					)}  size-6"
					id="rights-{shareOption.identity_id}-selection"
					required
					aria-label="Select rights"
					name="right"
					onclick={() => (selectionFocused = !selectionFocused)}
					onchange={(event) => {
						if (share) {
							share({
								resource_id: resourceId,
								identity_id: shareOption.identity_id,
								action: desiredActions(selectedAction).action,
								new_action: desiredActions(selectedAction).new_action
							});
							// if (closeShareMenu) {
							// 	closeShareMenu();
							// }
						} else {
							const form = (event.target as HTMLSelectElement).form;
							form?.requestSubmit();
						}
					}}
					bind:value={selectedAction}
				>
					{@render shareSelectOption(Action.OWN)}
					{@render shareSelectOption(Action.WRITE)}
					{@render shareSelectOption(Action.READ)}
					{@render shareSelectOption(undefined)}
				</select>
			</form>
			<span
				class="icon-[tabler--chevron-down] bg-secondary pointer-events-none absolute top-1/2 right-2 size-6 -translate-y-1/2 transition-transform duration-400"
				class:rotate-180={selectionFocused}
			>
			</span>
		</div> -->
	</div>
</li>

<style>
	.custom-select {
		&,
		&::picker(select) {
			appearance: base-select;
		}
	}
</style>
