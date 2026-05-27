<script lang="ts">
	import { getContext } from 'svelte';
	import type { Attachment } from 'svelte/attachments';
	import { SvelteSet } from 'svelte/reactivity';
	import type { Writable } from 'svelte/store';

	import { page } from '$app/state';
	import type { SidebarItem as SideBarItemType } from '$lib/types';
	import { initCollapse } from '$lib/userInterface';

	import SidebarItem from './SidebarItem.svelte';

	let {
		content,
		topLevel = false,
		onActiveChange
	}: {
		content: SideBarItemType;
		topLevel?: boolean;
		onActiveChange?: (active: boolean) => void;
	} = $props();
	let { id, name, pathname, hash, icon, items } = $derived({ ...content });
	let isFolder = $derived(
		Object.keys(content).includes('items') === true &&
			content &&
			((content as SideBarItemType).items?.length ?? 0) > 0
	);

	// Tracks ids of children that are currently active (for folders only).
	const activeChildIds = new SvelteSet<string>();
	let hasActiveChild = $derived(activeChildIds.size > 0);

	$effect(() => {
		// Notify parent that this item is active (directly or via an active child).
		onActiveChange?.((hasActiveChild && isFolder) || isActive);
	});

	const thisPage = $derived(pathname === page.url.pathname);
	let href = $derived(!hash ? pathname! : thisPage ? hash : `${pathname}${hash}`);
	// The id of the element, this SidebarItem links to (if any):
	let trackedElementId = $derived(href.startsWith('#') ? href.substring(1) : null);

	// Get context at top level during component initialization
	const scrollObserverContext = getContext<{
		observer: IntersectionObserver | undefined;
		activeSection: Writable<string | undefined>;
		visibleSections: Writable<Set<string>>;
	}>('scrollObserver');
	const activeSection = scrollObserverContext?.activeSection;
	const visibleSections = scrollObserverContext?.visibleSections;

	const addElementToObserver: Attachment = () => {
		if (scrollObserverContext?.observer) {
			// Get the element in the content that corresponds to this link and observe it
			const elementToObserve = trackedElementId ? document.getElementById(trackedElementId) : null;
			if (elementToObserve) {
				scrollObserverContext.observer.observe(elementToObserve);
				// Cleanup: unobserve when attachment is removed
				return () => scrollObserverContext.observer?.unobserve(elementToObserve);
			}
		}
	};

	// setting styling options for the link:
	let collapseControl: HTMLElement | null = $state(null);
	const isActive = $derived(
		isFolder
			? (trackedElementId && $activeSection === trackedElementId) || hasActiveChild
			: (trackedElementId && thisPage && $activeSection === trackedElementId) ||
					(thisPage && href !== hash)
	);
	const isVisible = $derived(
		(trackedElementId && thisPage && $visibleSections?.has(trackedElementId)) || false
	);
	const linkOpacity = $derived(isActive ? 'opacity-100' : isVisible ? 'opacity-95' : 'opacity-70');

	const toggleCollapse: Attachment<HTMLElement> = (node: HTMLElement) => {
		if (pathname === page.url.pathname || hasActiveChild) {
			const { element } = window.HSCollapse.getInstance(node, true);
			element.show();
		}
	};

	// needed somewhere?
	// initCollapse(document.getElementById(id + '-collapse')!);

	// Reactively open collapse when a child becomes active.
	// Note: do NOT re-run `initCollapse` on the collapse <ul> here. That <ul>
	// contains nested folders' chevron buttons (each with `data-collapse=...`);
	// re-running `HSCollapse.autoInit` on it re-scans those nested triggers and
	// leaves deeply-nested collapses in an inconsistent state ("stalled" /
	// unreachable). The <ul>'s own `{@attach initCollapse}` handles init once.
	$effect(() => {
		if (hasActiveChild && collapseControl) {
			const instance = window.HSCollapse.getInstance(collapseControl, true);
			if (instance?.element) {
				instance.element.show();
			}
		}
	});

	const openSidebar = () => {
		const { element } = window.HSOverlay.getInstance('#collapsible-mini-sidebar', true);
		element.open();
		window.HSStaticMethods.autoInit();
	};
</script>

{#snippet collapseList()}
	<ul
		id={id + '-collapse'}
		class="collapse {thisPage
			? 'open'
			: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
		aria-labelledby={id + '-control'}
		{@attach initCollapse}
	>
		{#each items as item (item.id)}
			<SidebarItem
				content={{
					...item,
					pathname: item.pathname || pathname
				} as SideBarItemType}
				onActiveChange={(active) => {
					if (active) {
						activeChildIds.add(item.id);
					} else {
						activeChildIds.delete(item.id);
					}
				}}
			/>
		{/each}
	</ul>
{/snippet}

<li class="space-y-0.5">
	<a
		{href}
		{@attach addElementToObserver}
		class="{isActive || (isFolder && hasActiveChild) || (!isFolder && isVisible)
			? 'text-base-content italic'
			: ' text-base-content-variant'} {!isFolder
			? 'flex'
			: ''} items-center gap-x-2 transition-opacity duration-600 hover:opacity-100 {linkOpacity}"
	>
		{#if topLevel}
			<span class="{icon} size-5"></span>
		{:else}
			<!-- Icon crossfade container -->
			<span class="relative inline-block size-6">
				<!-- Regular icon - fades out when active -->
				<span
					class="{icon} absolute inset-0 size-5 transition-opacity duration-600 {isActive
						? 'opacity-0'
						: 'opacity-100'}"
				></span>
				<!-- Active finger-pointing icon - fades in when active -->
				<span
					class="icon-[tabler--hand-finger-right] text-base-content/100 absolute inset-0 size-6 transition-opacity duration-600 {isActive
						? 'opacity-100'
						: 'opacity-0'}"
				></span>
			</span>
		{/if}
		<span class="overlay-minified:hidden">{name}</span>
		<!-- Chevron to open the collapse-->
		{#if isFolder}
			<button
				bind:this={collapseControl}
				type="button"
				class="btn btn-circle btn-sm btn-gradient btn-base-300 collapse-toggle {thisPage || isActive
					? 'open'
					: ''}"
				id={id + '-control'}
				data-collapse={'#' + id + '-collapse'}
				aria-label="Toggle folder collapse"
				onclick={(e) => {
					e.preventDefault();
					e.stopPropagation();
				}}
				{@attach toggleCollapse}
			>
				<span
					class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:hidden size-4 transition-all duration-300"
				></span>
				<span
					class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:block {topLevel
						? 'overlay-minified:rotate-270'
						: ''} hidden size-4 transition-all duration-300"
					role="button"
					tabindex="0"
					onclick={() => openSidebar()}
					onkeydown={() => openSidebar()}
				></span>
			</button>
		{/if}
	</a>
	{#if isFolder}
		{@render collapseList()}
	{/if}
</li>
