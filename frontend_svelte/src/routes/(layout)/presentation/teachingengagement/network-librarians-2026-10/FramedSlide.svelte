<script lang="ts">
	import Icon from '@iconify/svelte';
	import { type Snippet } from 'svelte';

	// import { SvelteMap } from 'svelte/reactivity';

	let {
		children,
		part,
		color = 'secondary',
		section,
		// title,
		coloring,
		hideProgressBar = false,
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
		hideProgressBar?: boolean;
		debug?: boolean;
	} = $props();

	type ContentItem = {
		part: string;
		icon?: string;
		title: string;
	};
	let content: ContentItem[] = [
		{
			part: 'checkin',
			// icon: 'akar-icons:map',
			title: 'Check in'
		},
		{
			part: 'overview',
			// icon: 'akar-icons:map',
			title: 'Overview'
		},
		{
			part: 'context',
			icon: 'stash:circle-dot',
			title: 'Context'
		},
		{
			part: 'inspiration',
			icon: 'glyphs:books-bold',
			title: 'Inspiration'
		},
		{
			part: 'implementation',
			icon: 'carbon:development',
			title: 'Implementation'
		},
		{
			part: 'results',
			icon: 'bi:bar-chart',
			title: 'Results'
		},
		{
			part: 'comments-and-questions',
			title: 'Comments / Questions?'
		}
	];
	const thisContent = content.findIndex((item) => item.part === part);

	// TBD: should no longer be necessary after swichting to iconify/icon?
	// Tailwind safelist: border-primary border-primary-container border-secondary border-secondary-container border-accent border-accent-container border-warning border-warning-container border-error border-error-container border-success border-success-container border border-info border-info-container border-neutral border-neutral-container
</script>

{#snippet progressBar()}
	<div class="fixed-progress-header flex w-full items-center gap-4 px-10">
		{#each content as item, index (index)}
			{#if item.icon}
				<div class="flex items-center gap-4 {index < content!.length - 1 ? 'grow' : ''}">
					<a href={'#' + item.part} aria-label={item.title}>
						<div
							class="border-{color} shadow-base-shadow flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-full border-4 bg-transparent shadow-lg"
						>
							<Icon
								class="text-{color} {index < thisContent + 1 ? '' : 'opacity-20'}"
								icon={item.icon}
							/>
						</div>
					</a>
					{#if index < content!.length - 1}
						<div class="bg-{color} shadow-{color} h-2 grow rounded shadow-lg"></div>
					{/if}
				</div>
			{/if}
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
				<div
					class="relative mr-[800px] h-[100px] flex-shrink-0 text-7xl {debug
						? 'border-4 border-blue-800'
						: ''} p-1"
				>
					<div class="text-{color} text-left font-bold">
						{content.find((item) => item.part === part)?.title}
					</div>
				</div>
				{#if !hideProgressBar}
					<div
						class="absolute right-0 h-[100px] w-[800px] {debug ? 'border-4 border-red-400' : ''}"
					>
						{@render progressBar()}
					</div>
				{/if}
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
