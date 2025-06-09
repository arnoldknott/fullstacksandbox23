<script lang="ts">
	type Identity = {
		id: string;
		name: string;
		right: string;
	};

	let { resourceId, icon, identity }: { resourceId: string; icon: string; identity: Identity } =
		$props();

	const rightsIcon = (right: string) => {
		return right === 'own'
			? 'icon-[tabler--key-filled] bg-success'
			: right === 'write'
				? 'icon-[material-symbols--edit-outline-rounded] bg-warning'
				: right === 'read'
					? 'icon-[tabler--eye] bg-neutral'
					: 'icon-[tabler--ban] bg-error';
	};
</script>

{#snippet shareButton(newAction: string)}
	<li>
		<button
			data-sveltekit-preload-data={false}
			class="btn dropdown-item btn-text max-w-40 content-center"
			name="id"
			type="submit"
			value={resourceId}
			formaction="?/share&identity-id={identity.id}&action={identity.right}&new-action={newAction}"
			aria-label={newAction}
		>
			<span class={rightsIcon(newAction)}></span>
		</button>
	</li>
{/snippet}

<li>
	<div class="tooltip flex items-center">
		<div
			class="dropdown-item text-secondary tooltip-toggle w-full max-w-42 content-center"
			aria-label={identity.name}
		>
			<span class="{icon} shrink-0"></span>
			{identity.name.slice(0, 12)}{identity.name.length > 13 ? ' ...' : null}
			{#if identity.name.length > 12}
				<span
					class="tooltip-content tooltip-shown:visible tooltip-shown:opacity-100 bg-base-300"
					role="tooltip"
				>
					{identity.name}
				</span>
			{/if}
		</div>
		<div class="mr-2">
			<span class="{rightsIcon(identity.right)} ml-2 size-4"></span>
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
				{@render shareButton('own')}
				{@render shareButton('write')}
				{@render shareButton('read')}
				{@render shareButton('unshare')}
			</ul>
		</div>
	</div>
</li>
