<script lang="ts">
	import type { HSDropdown } from 'flyonui/flyonui';
	let {
		icon,
		name,
		right = $bindable(),
		parentMenus
	}: { icon: string; name: string; right: string; parentMenus?: HSDropdown[] } = $props();

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

<li>
	<div class="text-secondary tooltip flex items-center">
		<div
			class="dropdown-item text-secondary tooltip-toggle w-full max-w-42 content-center"
			aria-label={name}
		>
			<span class="icon-[{icon}] mr-2 shrink-0"></span>
			{name.slice(0, 12)}{name.length > 13 ? ' ...' : null}
			{#if name.length > 12}
				<span
					class="tooltip-content tooltip-shown:visible tooltip-shown:opacity-100 bg-base-300"
					role="tooltip"
				>
					{name}
				</span>
			{/if}
		</div>
		<div class="mr-2">
			<!-- {rightsIconSelection(team.id) ? "bg-success" : ""} -->
			<span class="{rightsIcon(right)} ml-2 size-4"></span>
		</div>
		<div class="dropdown relative inline-flex [--offset:0] [--placement:left-start]">
			<button
				id="rights"
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
				aria-labelledby="rights"
			>
				<li>
					<button
						data-sveltekit-preload-data={false}
						class="btn dropdown-item btn-text max-w-40 content-center"
						name="id"
						type="submit"
						onclick={() => {
							right = 'own';
							parentMenus?.forEach((menu: HSDropdown) => {
								menu.close();
							});
						}}
						aria-label="own"><span class="icon-[tabler--key-filled] bg-success"></span></button
					>
				</li>
				<li>
					<button
						data-sveltekit-preload-data={false}
						class="btn dropdown-item btn-text max-w-40 content-center"
						name="id"
						type="submit"
						onclick={() => {
							right = 'write';
							parentMenus?.forEach((menu: HSDropdown) => {
								menu.close();
							});
						}}
						aria-label="write"
						><span class="icon-[material-symbols--edit-outline-rounded] bg-warning"></span>
					</button>
				</li>
				<li>
					<button
						data-sveltekit-preload-data={false}
						class="btn dropdown-item btn-text max-w-40 content-center"
						name="id"
						type="submit"
						onclick={() => {
							right = 'read';
							parentMenus?.forEach((menu: HSDropdown) => {
								menu.close();
							});
						}}
						aria-label="read"
						><span class="icon-[tabler--eye] bg-neutral"></span>
					</button>
				</li>
				<li>
					<button
						data-sveltekit-preload-data={false}
						class="btn dropdown-item btn-text max-w-40 content-center"
						name="id"
						type="submit"
						onclick={() => {
							right = '';
							parentMenus?.forEach((menu: HSDropdown) => {
								menu.close();
							});
						}}
						aria-label="remove share"
						><span class="icon-[tabler--ban] bg-error"></span>
					</button>
				</li>
			</ul>
		</div>
		<!-- <div class={rightsIconSelection(team.id) ? 'block' : 'invisible'}>
			<span class="icon-[openmoji--check-mark]"></span>
		</div> -->
	</div>
</li>
