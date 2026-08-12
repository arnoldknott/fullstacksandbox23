<script lang="ts">
	import { getContext } from 'svelte';
	import type { Attachment } from 'svelte/attachments';
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

	// Tracks active state of each child by id (for folders only). Plain `$state`
	// record so mutations from child-component callbacks reliably re-trigger
	// `$derived`s and template class bindings in this component.
	let activeChildMap = $state<Record<string, boolean>>({});
	let hasActiveChild = $derived(Object.values(activeChildMap).some(Boolean));

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

	// Auto-expand the chain to an active descendant on sidebar-driven navigation.
	//
	// We let FlyonUI fully own the `open`/`hidden` classes on both the chevron
	// toggle button AND the collapse <ul>; Svelte must NOT toggle those classes
	// reactively, otherwise FlyonUI's `show()`/`hide()` guards (which check
	// `el.classList.contains("open")` on the toggle, and `content.classList.
	// contains("hidden")` on the <ul>) get out of sync and click-to-toggle stops
	// working (or `show()` bails as a no-op and the chain stays collapsed).
	//
	// Strategy: use the static `HSCollapse.show()` (idempotent: only acts when
	// content still has `hidden`). Trigger on every navigation, gated by
	// `lastAutoShowPath` so transient scroll-driven `activeSection` changes
	// don't re-open a manually-closed folder.
	let lastAutoShowPath: string | null = null;
	$effect(() => {
		const path = page.url.pathname;
		// Read these so the effect re-runs when descendants finish reporting up.
		const shouldShow = thisPage || hasActiveChild;
		if (!shouldShow || !collapseControl) return;
		if (path === lastAutoShowPath) return;
		if (typeof window === 'undefined' || !window.HSCollapse) return;
		const instance = window.HSCollapse.getInstance(collapseControl, true);
		if (instance?.element) {
			instance.element.show();
		}
		// window.HSCollapse.show(collapseControl);
		lastAutoShowPath = path;
	});

	const openSidebar = () => {
		const { element } = window.HSOverlay.getInstance('#collapsible-mini-sidebar', true);
		element.open();
		window.HSStaticMethods.autoInit();
	};
</script>

{#snippet collapseList()}
	<!--
		Initial class is `hidden`; FlyonUI's `HSCollapse.show()` removes `hidden`
		and adds `open`. Svelte must not touch these classes reactively (see effect
		above). The auto-expand effect calls `show()` on mount when a descendant
		is active, so the chain expands on direct URL load too.
	-->
	<ul
		id={id + '-collapse'}
		class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
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
					activeChildMap[item.id] = active;
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
			<!--
				Do NOT bind the `open` class reactively here. FlyonUI's `HSCollapse`
				manages it on this toggle in lockstep with the `<ul>` content; any
				Svelte-controlled `open` here desyncs the two and breaks click-toggle
				(see `hide()`/`show()` guards in `flyonui/dist/collapse.mjs`).
			-->
			<button
				bind:this={collapseControl}
				type="button"
				class="btn btn-circle btn-sm btn-gradient btn-base-300 collapse-toggle"
				id={id + '-control'}
				data-collapse={'#' + id + '-collapse'}
				aria-label="Toggle folder collapse"
				onclick={(e) => {
					e.preventDefault();
					e.stopPropagation();
				}}
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
