<script lang="ts">
	import { type Snippet } from 'svelte';
	// import { SvelteMap } from 'svelte/reactivity';

	let {
		children,
		part,
		color,
		section,
		// title,
		coloring,
		footer,
		debug
	}: {
		children: Snippet;
		part?: string;
		color?: string;
		section?: string;
		// title?: string;
		coloring?: { background: string; text: string };
		footer?: Snippet;
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
			part: 'motivation',
			icon: 'icon-[vaadin--thumbs-up-o]',
			title: 'Motivation'
		},
		{
			part: 'diversity',
			icon: 'icon-[material-symbols--diversity-1-rounded]',
			title: 'Diversity'
		},
		{
			part: 'overview',
			icon: 'icon-[grommet-icons--overview]',
			title: 'Overview'
		}
	];
	const thisContent = content.findIndex((item) => item.part === part);
	// let contentColor = new SvelteMap([
	// 	['context', 'error'],
	// 	['tension', 'warning'],
	// 	['stories', 'neutral']
	// ]);

	// Tailwind safelist: border-primary border-primary-container border-secondary border-secondary-container border-accent border-accent-container border-warning border-warning-container border-error border-error-container border-success border-success-container border border-info border-info-container border-neutral border-neutral-container
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
							class="{item.icon} size-10 bg-{color} {index < thisContent + 1 ? '' : 'opacity-20'}"
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

<section
	id={!section ? part : part + '-' + section}
	data-background-color={coloring ? coloring.background : ''}
	class="r-stretch"
>
	<!-- style: directive (not style="...") so it only sets `color` and does not clobber the width/height Reveal.js sets imperatively on .r-stretch -->
	<div class="r-stretch" style:color={coloring ? coloring.text : 'var(--color-base-content)'}>
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
				// class="relative flex min-h-0 grow flex-col items-center justify-center {debug
				// 	? 'border-4 border-green-400'
				// 	: ''}"
				// class=" {debug ? 'border-4 border-green-400' : ''}"
				// class="relative mt-[100px] flex grow flex-col items-center {debug
				class="flex min-h-0 flex-1 flex-col justify-center {debug
					? 'border-4 border-green-400'
					: ''}"
			>
				{@render children?.()}
			</div>
		</div>
		<div class="absolute right-0 bottom-0 mr-20 p-2">
			{#if footer}
				{@render footer?.()}
			{/if}
			<!-- {#if part}
				<span class="font-bold">{part}</span>
			{/if}
			{#if section}
				<span class="font-bold"> - {section}</span>
			{/if} -->
		</div>
	</div>
</section>
