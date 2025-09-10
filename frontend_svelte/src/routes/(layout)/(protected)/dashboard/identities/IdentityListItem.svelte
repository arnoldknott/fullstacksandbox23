<script lang="ts">
	import type { AnyGroupIdentity } from '$lib/types';
	import IdBadge from '../IdBadge.svelte';
	let {
		identity,
		link,
		unlink,
		remove
	}: {
		identity: AnyGroupIdentity;
		link?: (id: string) => void;
		unlink?: (id: string) => void;
		remove?: (id: string) => void;
	} = $props();
</script>

{#snippet listContent()}
	<dt class="text-base-content title-small flex-1">
		<IdBadge id={identity.id} />
		{identity.name}
	</dt>
	<dd class="text-base-content/80 mt-1 flex-2">
		{identity.description}
	</dd>
{/snippet}

<div class="px-4 py-6 text-base sm:flex sm:flex-row sm:gap-4 sm:px-0">
	{#if link}
		<button class="w-full text-left sm:flex sm:flex-row" onclick={() => link?.(identity.id)}>
			{@render listContent()}
		</button>
	{:else}
		{@render listContent()}
	{/if}
	<dd class="flex-none">
		<div class="flex flex-row gap-3">
			<a
				id="info-about-{identity.id}"
				href="/dashboard/identities/group/{identity.id}"
				aria-label="Info about {identity.name}"
			>
				<button
					class="btn btn-info-container btn btn-circle btn-gradient shadow-outline shadow-md"
					aria-labelledby="info-about-{identity.id}"
				>
					<span class="icon-[tabler--info-triangle]"></span>
				</button>
			</a>
			{#if unlink}
				<button
					class="btn btn-warning-container btn-circle btn-gradient shadow-outline shadow-md"
					aria-label="Unlink {identity.name}"
					onclick={() => unlink(identity.id)}
				>
					<span class="icon-[tabler--link-off]"></span>
				</button>
			{/if}
			{#if remove}
				<button
					class="btn btn-error-container btn-circle btn-gradient shadow-outline shadow-md"
					aria-label="Remove {identity.name}"
					onclick={() => remove(identity.id)}
				>
					<span class="icon-[tabler--trash]"></span>
				</button>
			{/if}
		</div>
	</dd>
</div>
