<script lang="ts">
	import { Action, IdentityType, AccessHandler } from '$lib/accessHandler';

	// TBD: consider moving this to a types.d.ts file
	type Identity = {
		id: string;
		name: string;
		type: IdentityType;
		accessRight: Action | null;
	};

	let {
		resourceId,
		identity,
		share
	}: {
		resourceId: string;
		identity: Identity;
		share?: (identityId: string, action: Action | null, newAction: Action) => void;
	} = $props();
</script>

{#snippet shareButton(newAction: Action)}
	<li>
		<button
			data-sveltekit-preload-data={false}
			class="btn dropdown-item btn-text max-w-40 content-center"
			name="id"
			type="submit"
			value={resourceId}
			formaction={!share
				? `?/share&identity-id=${identity.id}&action=${identity.accessRight}&new-action=${newAction}`
				: undefined}
			onclick={share ? () => share(identity.id, identity.accessRight, newAction) : undefined}
			aria-label={String(newAction)}
		>
			<span class={AccessHandler.rightsIcon(newAction)}></span>
		</button>
	</li>
{/snippet}

<li>
	<div class="tooltip flex items-center [--placement:top]">
		<div
			class="dropdown-item text-secondary tooltip-toggle max-w-42 w-full content-center"
			aria-label={identity.name}
		>
			<span class="{AccessHandler.identityIcon(identity.type)} shrink-0"></span>
			{identity.name.slice(0, 12)}{identity.name.length > 13 ? ' ...' : null}
			{#if identity.name.length > 12}
				<span
					class="tooltip-content tooltip-shown:visible tooltip-shown:opacity-100 bg-base-300 rounded-xl outline"
					role="tooltip"
				>
					{identity.name}
				</span>
			{/if}
		</div>
		<div class="mr-2">
			<span class="{AccessHandler.rightsIcon(identity.accessRight)} ml-2 size-4"></span>
		</div>
		<div class="dropdown relative inline-flex [--offset:0] [--placement:left-start]">
			<button
				id="rights-{identity.id}"
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
				aria-labelledby="rights-{identity.id}"
			>
				{@render shareButton(Action.OWN)}
				{@render shareButton(Action.WRITE)}
				{@render shareButton(Action.READ)}
				{@render shareButton(Action.UNSHARE)}
			</ul>
		</div>
	</div>
</li>
