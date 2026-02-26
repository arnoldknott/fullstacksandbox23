<script lang="ts">
	import { type Snippet } from 'svelte';
	import { SvelteMap } from 'svelte/reactivity';

	let {
		children,
		section,
		content,
		debug
	}: {
		children: Snippet;
		section?: 'old' | 'new';
		content?: string[];
		debug?: boolean;
	} = $props();
	// let color = $derived(symbol === 'history' ? 'info' : symbol === '' ? 'secondary' : 'success');
	let icon = $state(
		section === 'old'
			? 'icon-[game-icons--greek-temple]'
			: section === 'new'
				? 'icon-[healthicons--i-exam-multiple-choice-outline]'
				: ''
	);
	let color = $state(section === 'old' ? 'secondary' : section === 'new' ? 'primary' : 'info');
	let contentIcons = new SvelteMap([
		['automation', 'icon-[streamline-plump--cog-automation]'],
		['design', 'icon-[tabler--palette]'],
		['motivation', 'icon-[f7--book]'],
		['implementation', 'icon-[ri--tools-fill]'],
		['results', 'icon-[uim--graph-bar]'],
		['outlook', 'icon-[lsicon--view-outline]']
	]);
	let contentColor = new SvelteMap([
		['automation', 'error'],
		['design', 'warning'],
		['motivation', 'neutral'],
		['implementation', 'info'],
		['results', 'accent'],
		['outlook', 'primary']
	]);

	// Tailwind safelist: border-primary border-secondary border-accent border-warning border-error border-success border-info border-neutral
</script>

{#snippet progressBar()}
	<div class="fixed-progress-header flex w-full items-center gap-4 px-10">
		{#each content as item, index (index)}
			<div class="flex items-center gap-4 {index < content!.length - 1 ? 'grow' : ''}">
				<div
					class="border-{contentColor.get(item) ||
						color} border-4 bg-transparent shadow-{contentColor.get(
						item
					)} flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-full shadow-lg"
				>
					{#if index < content!.length}
						<!-- <span class="text-{color}-content font-bold">{item}</span> -->
						<span class="{contentIcons.get(item) || color} size-14 bg-{contentColor.get(item)}"
						></span>
					{/if}
				</div>
				{#if index < content!.length}
					<div class="bg-{color} shadow-{color} h-2 grow rounded shadow-lg"></div>
				{/if}
			</div>
		{/each}
	</div>
{/snippet}

<section>
	<div class="r-stretch">
		<div
			class="relative flex h-full w-full flex-col gap-1 {debug
				? 'border-4 border-orange-400'
				: ''} p-1"
		>
			{#if icon}
				<div
					class="absolute h-[100px] w-[200px] text-8xl {debug
						? 'border-4 border-blue-800'
						: ''} p-1"
				>
					<span class="{icon} size-22 bg-{color}"></span>
					<!-- <img src="/teachingevolution/{symbol}.png" alt="{symbol}" class="h-full w-full" /> -->
				</div>
			{/if}
			{#if content}
				<div
					class="relative ml-[200px] h-[100px] flex-shrink-0 {debug
						? 'border-4 border-red-400'
						: ''}"
				>
					{@render progressBar()}
				</div>
			{/if}
			<div
				class="flex min-h-0 grow flex-col items-center justify-center {debug
					? 'border-4 border-green-400'
					: ''}"
			>
				{@render children?.()}
			</div>
		</div>
	</div>
</section>
