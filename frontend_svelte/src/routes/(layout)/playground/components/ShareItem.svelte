<script lang="ts">
	import { Action, AccessHandler } from '$lib/accessHandler';
	import type { AccessPolicy, AccessShareOption } from '$lib/types';

	let {
		resourceId,
		shareOption,
		share
	}: {
		resourceId: string;
		shareOption: AccessShareOption;
		share?: (accessPolicy: AccessPolicy) => void;
	} = $props();

	const desiredActions = (selectedAction?: Action) => {
		let action = shareOption.action;
		let newAction = undefined;
		// deleting access policy:
		if (selectedAction === undefined) {
			action = undefined;
			newAction = undefined;
		}
		// creating a new access policy:
		else if (shareOption.action === undefined) {
			action = selectedAction;
		}
		// updating an existing access policy:
		else if (selectedAction && shareOption.action !== selectedAction) {
			newAction = selectedAction;
		}
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
			class="btn dropdown-item btn-text max-w-40 content-center"
			name="id"
			type="submit"
			value={resourceId}
			formaction={!share
				? `?/share&identity-id=${shareOption.identity_id}&action=${desiredActions(selectedAction).action}&new-action=${desiredActions(selectedAction).new_action}`
				: undefined}
			onclick={() => {
				console.log('=== Trying to change access policy ===');
				console.log('=== resourceId ===', resourceId);
				console.log('=== shareOption ===', shareOption);
				console.log('=== newAction ===', selectedAction);
				console.log('=== desiredActions ===', desiredActions(selectedAction));
				// share
				// 	? () =>
				// 			share({
				// 				resource_id: resourceId,
				// 				identity_id: shareOption.identity_id,
				// 				action: shareOption.action,
				// 				new_action: newAction
				// 			})
				// 	: undefined
			}}
			aria-label={String(selectedAction) || 'remove'}
		>
			<span class={AccessHandler.rightsIcon(selectedAction)}></span>
		</button>
	</li>
{/snippet}

<li>
	<div class="tooltip flex items-center [--placement:top]">
		<div
			class="dropdown-item text-secondary tooltip-toggle max-w-42 w-full content-center"
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
	</div>
</li>
