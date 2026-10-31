<script lang="ts">
	import Icon from '@iconify/svelte';
	import { slide } from 'svelte/transition';

	let {
		title,
		content,
		color = 'primary'
	}: { title: string; content: string[]; color?: string } = $props();

	let showContent = $state(false);
</script>

<dl>
	<dt class="font-bold">
		<div class="flex justify-between">
			<span class="text-4xl">{title}</span>
			<button
				type="button"
				class="btn btn-circle btn-sm btn-{color}-container btn-gradient mr-2 self-center"
				aria-label="Toggle inputs"
				aria-expanded={showContent}
				onclick={() => (showContent = !showContent)}
			>
				<Icon
					icon="tabler:chevron-down"
					class="{showContent ? 'rotate-180' : ''} size-7 transition-all duration-300"
				/>
				<Icon
					icon="tabler:chevron-down"
					class="{!showContent ? 'rotate-180' : ''} hidden size-7 transition-all duration-300"
					role="button"
				/>
			</button>
		</div>
	</dt>
	{#if showContent}
		{#each content as item, index (index)}
			<dd class="mb-2" class:mt-3={index === 0} transition:slide={{ duration: 600 }}>
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html item}
			</dd>
		{/each}
	{/if}
</dl>
