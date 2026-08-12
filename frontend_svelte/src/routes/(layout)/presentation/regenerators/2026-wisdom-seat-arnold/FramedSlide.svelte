<script lang="ts">
	import { type Snippet } from 'svelte';
	// import { SvelteMap } from 'svelte/reactivity';

	let {
		children,
		part,
		color,
		section,
		// title,
		debug
	}: {
		children: Snippet;
		part?: string;
		color?: string;
		section?: string;
		// title?: string;
		debug?: boolean;
	} = $props();
	// let color = $derived(symbol === 'history' ? 'info' : symbol === '' ? 'secondary' : 'success');
	// let icon = $derived(
	// 	section === 'old'
	// 		? 'icon-[game-icons--greek-temple]'
	// 		: section === 'new'
	// 			? 'icon-[healthicons--i-exam-multiple-choice-outline]'
	// 			: ''
	// );
	// let color = $derived(section === 'old' ? 'secondary' : section === 'new' ? 'primary' : 'info');
	// let content = new SvelteMap([
	// 	['context', 'icon-[stash--circle-dot]'],
	// 	['tension', 'icon-[mingcute--lightning-fill]'],
	// 	['stories', 'icon-[f7--chat-bubble-2-fill]']
	// ]);
	let content = [
		{
			part: 'context',
			icon: 'icon-[stash--circle-dot]',
			title: 'Context'
		},
		{
			part: 'tension',
			icon: 'icon-[mingcute--lightning-fill]',
			title: 'Tension'
		},
		{
			part: 'stories',
			icon: 'icon-[f7--chat-bubble-2-fill]',
			title: 'Stories'
		}
	];
	const thisContent = content.findIndex((item) => item.part === part);
	// let contentColor = new SvelteMap([
	// 	['context', 'error'],
	// 	['tension', 'warning'],
	// 	['stories', 'neutral']
	// ]);

	// Tailwind safelist: border-primary border-secondary border-accent border-warning border-error border-success border-info border-neutral
</script>

{#snippet progressBar()}
	<div class="fixed-progress-header flex w-full items-center gap-4 px-10">
		{#each content as item, index (index)}
			<div class="flex items-center gap-4 {index < content!.length - 1 ? 'grow' : ''}">
				<a href={'#' + item.part} aria-label={item.title}>
					<div
						class="border-{color} shadow-base-shadow flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-full border-4 bg-transparent shadow-lg"
					>
						<!-- {#if index < content!.length - 1} -->
						<!-- {#if index < thisContent + 1} -->
						<!-- <span class="text-{color}-content font-bold">{item}</span> -->
						<!-- <span class="{content.get(item)} size-14 bg-{color}"></span> -->
						<span
							class="{item.icon} size-14 bg-{color} {index < thisContent + 1 ? '' : 'opacity-20'}"
						></span>
						<!-- {/if} -->
					</div>
				</a>
				{#if index < content!.length - 1}
					<div class="bg-{color} shadow-{color} h-2 grow rounded shadow-lg"></div>
				{/if}
			</div>
		{/each}
	</div>
{/snippet}

<section id={!section ? part : part + '-' + section}>
	<div class="r-stretch">
		<div
			class="relative flex h-full w-full flex-col gap-1 {debug
				? 'border-4 border-orange-400'
				: ''} p-3"
		>
			{#if thisContent >= 0}
				<div class="absolute h-[100px] w-[600px] {debug ? 'border-4 border-red-400' : ''}">
					{@render progressBar()}
				</div>
				<!-- {/if}
			{#if title} -->
				<div
					class="relative ml-[600px] h-[100px] flex-shrink-0 text-7xl {debug
						? 'border-4 border-blue-800'
						: ''} p-1"
				>
					<!-- <span class="{icon} size-22 bg-{color}"></span> -->
					<div class="text-{color} text-left font-bold">
						{content.find((item) => item.part === part)?.title}
					</div>
				</div>
			{/if}

			<div
				class="relative flex min-h-0 grow flex-col items-center justify-center {debug
					? 'border-4 border-green-400'
					: ''}"
			>
				<!-- consider also class: content-center -->
				{@render children?.()}
			</div>
		</div>
	</div>
</section>
