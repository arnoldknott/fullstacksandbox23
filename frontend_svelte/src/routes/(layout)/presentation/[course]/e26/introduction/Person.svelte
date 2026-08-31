<script lang="ts">
	import type { Snippet } from 'svelte';

	import NodeOverlay from './NodeOverlay.svelte';

	let {
		placement,
		name,
		cardHeader,
		cardPlacement,
		pictureLink,
		children
	}: {
		placement: string;
		name: string;
		cardHeader: string;
		cardPlacement?: string;
		pictureLink?: URL;
		children: Snippet;
	} = $props();
</script>

<div class="pointer-events-auto absolute {placement} h-80 w-180">
	<NodeOverlay
		buttonExtraClasses="btn-secondary rounded-[50%]  h-50"
		cardExtraClasses="bg-secondary-container text-secondary-container-content {cardPlacement} text-4xl"
	>
		{#snippet buttonText()}
			{name}
		{/snippet}
		{#snippet header()}
			<div class="text-left text-5xl font-bold">{cardHeader}</div>
		{/snippet}
		<div class="flex flex-row gap-4">
			{@render children()}
			{#if pictureLink}
				<img
					src={pictureLink.toString()}
					alt={name}
					class="h-auto w-40 mask-y-from-85% mask-y-to-100% mask-x-from-75% mask-x-to-100% object-contain opacity-70"
				/>
			{/if}
		</div>
	</NodeOverlay>
</div>
