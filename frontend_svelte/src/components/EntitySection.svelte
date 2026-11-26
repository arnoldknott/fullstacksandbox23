<script lang="ts">
	import type { Snippet } from 'svelte';

	import Card from '$components/Card.svelte';
	import Title from '$components/Title.svelte';

	const viewOrder = ['preview', 'grid', 'list', 'table'] as const;
	type EntityView = (typeof viewOrder)[number];

	let {
		id,
		title,
		entityLabel,
		viewMode = $bindable<EntityView>('table'),
		hideNew = $bindable(true),
		hasPending = false,
		children,
		table,
		grid,
		list,
		preview
	}: {
		id: string;
		title: string;
		entityLabel: string;
		viewMode?: EntityView;
		hideNew?: boolean;
		hasPending?: boolean;
		children?: Snippet;
		table?: Snippet;
		grid?: Snippet;
		list?: Snippet;
		preview?: Snippet;
	} = $props();

	const viewSnippets: Record<EntityView, Snippet | undefined> = $derived({
		table,
		grid,
		list,
		preview
	});
	const availableViews = $derived(viewOrder.filter((view) => viewSnippets[view]));

	$effect(() => {
		if (!availableViews.includes(viewMode)) {
			viewMode = availableViews[0] ?? 'table';
		}
	});
</script>

<Card {id} {title} extraClasses="label-large">
	{#snippet header()}
		<div class="flex justify-between">
			<Title id={`${id}-overview`} class="grow">Overview</Title>
			<div class="flex flex-row items-center justify-center">
				{#if hideNew || !hasPending}
					<button
						class="btn btn-primary-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
						aria-label={`Add new ${entityLabel}`}
						onclick={() => (hideNew = false)}
					>
						<span class="icon-[fa6-solid--plus] size-5"></span>
						<span class="hidden sm:inline">Add new</span>
						<span class="hidden md:inline">{entityLabel}</span>
					</button>
				{/if}
				{#if availableViews.length > 1}
					<div class="join shadow-outline rounded-full shadow-sm">
						{#each availableViews as view, index (view)}
							<button
								aria-label={view.charAt(0).toUpperCase() + view.slice(1)}
								class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline py-4 shadow"
								class:rounded-l-full={index === 0}
								class:rounded-r-full={index === availableViews.length - 1}
								class:opacity-60={viewMode !== view}
								onclick={() => (viewMode = view)}
							>
								{#if view === 'table'}
									<span class="icon-[material-symbols--table-outline] size-5"></span>
								{:else if view === 'grid'}
									<span class="icon-[gridicons--grid] size-5"></span>
								{:else if view === 'list'}
									<span class="icon-[material-symbols--view-list-outline] size-5"></span>
								{:else}
									<span class="icon-[material-symbols--preview-outline] size-5"></span>
								{/if}
							</button>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/snippet}
	{@render children?.()}
	{#each availableViews as view (view)}
		<div class:hidden={viewMode !== view} class="w-full overflow-x-auto">
			{@render viewSnippets[view]?.()}
		</div>
	{/each}
</Card>
