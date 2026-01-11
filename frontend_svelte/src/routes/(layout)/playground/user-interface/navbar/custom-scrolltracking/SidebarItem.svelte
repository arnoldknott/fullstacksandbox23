<script lang="ts">
	// import type { SidebarItemContent, SidebarFolderContent } from '$lib/types';
	import type { SidebarFolderContent } from '$lib/types';
	import type { SidebarItem as SideBarItemType } from '$lib/types';
	import SidebarItem from './SidebarItem.svelte';
	import { getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { Attachment } from 'svelte/attachments';
	import { initCollapse } from '$lib/userInterface';
	import { page } from '$app/state';
	import SidebarFolder from './SidebarFolder.svelte';
	import SidebarLink from './SidebarLink.svelte';

	let {
		content,
		topLevel = false,
		isActiveChild = $bindable(false)
	}: {
		content: SideBarItemType;
		topLevel?: boolean;
		isActiveChild?: boolean;
	} = $props();
	let { id, name, pathname, hash, icon, items } = $derived({ ...content });
	let isFolder = $derived(
		Object.keys(content).includes('items') === true &&
			content &&
			((content as SideBarItemType).items?.length ?? 0) > 0
	);

	// this variable tracks if any child item is active:
	let hasActiveChild = $state(false);

	// this variable tracks active states of all children (for folders only):
	let childActiveStates: boolean[] = $state(content.items?.map(() => false) ?? []);

	$effect(() => {
		// communicates to parent (via bindable), that this folder is active because one of its children is active:
		isActiveChild = (hasActiveChild && isFolder) || isActive;
		// Checks if any of this folders children are active:
		hasActiveChild = childActiveStates.some((active) => active);
	});

	const thisPage = $derived.by(() => (pathname: string) => pathname === page.url.pathname);
	const createHref = $derived.by(() => (destinationPathname: string, hash?: string) => {
		let href = '';
		if (!hash) href = destinationPathname;
		else if (thisPage(destinationPathname)) {
			href = hash;
		} else href = `${destinationPathname}${hash}`;
		return href;
	});
	let href = $derived(createHref(pathname!, hash));
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
			: (trackedElementId && thisPage(pathname!) && $activeSection === trackedElementId) ||
					(thisPage(pathname!) && href !== hash)
	);
	const isVisible = $derived(
		(trackedElementId && thisPage(pathname!) && $visibleSections?.has(trackedElementId)) || false
	);
	const linkOpacity = $derived(isActive ? 'opacity-100' : isVisible ? 'opacity-95' : 'opacity-70');

	const toggleCollapse: Attachment<HTMLElement> = (node: HTMLElement) => {
		// collapseControl = node;
		// if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
		// if (page.url.pathname === node.dataset.pathname) {
		if (pathname === page.url.pathname || hasActiveChild) {
			const { element } = window.HSCollapse.getInstance(node, true);
			element.show();
		}
	};

	// needed somewhere?
	// initCollapse(document.getElementById(id + '-collapse')!);

	// Reactively open collapse when a child becomes active
	$effect(() => {
		if (hasActiveChild && collapseControl) {
			const instance = window.HSCollapse.getInstance(collapseControl, true);
			if (instance?.element) {
				// or should the show be on document.getElementById(id + '-collapse')?
				instance.element.show();
				// TBD: initCollapse here?
				initCollapse(document.getElementById(id + '-collapse')!);
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
		class="collapse {thisPage(pathname!)
			? 'open'
			: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
		aria-labelledby={id + '-control'}
		{@attach initCollapse}
	>
		{#each items as item, index (item.id)}
			<SidebarItem
				content={{
					...item,
					pathname: item.pathname || pathname
				} as SidebarFolderContent}
				bind:isActiveChild={childActiveStates[index]}
			/>
		{/each}
	</ul>
{/snippet}

<!-- {#if isFolder} -->
<!-- It's a Folder -->
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
		{#if isFolder}
			<button
				bind:this={collapseControl}
				type="button"
				class="btn btn-circle btn-sm btn-gradient btn-base-300 collapse-toggle {thisPage(
					pathname!
				) || isActive
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
<!-- It's a Link -->
<!-- {:else} 
	<li>
		<a
			{href}
			{@attach addElementToObserver}
			class="{isActive || isVisible
				? 'text-base-content italic'
				: ' text-base-content-variant'} flex items-center gap-x-2 transition-opacity duration-600 hover:opacity-100 {linkOpacity}"
		>
			{#if topLevel}
				<span class="{icon} size-5"></span>
			{:else}
				<span class="relative inline-block size-6">
					<span
						class="{icon} absolute inset-0 size-5 transition-opacity duration-600 {isActive
							? 'opacity-0'
							: 'opacity-100'}"
					></span>
					<span
						class="icon-[tabler--hand-finger-right] text-base-content/100 absolute inset-0 size-6 transition-opacity duration-600 {isActive
							? 'opacity-100'
							: 'opacity-0'}"
					></span>
				</span>
			{/if}
			<span class="overlay-minified:hidden">{name}</span>
		</a>
	</li>
{/if} -->

<!-- Is the SidebarItem a Link or a Folder?
{#if Object.keys(content).includes('items') === false || (content as SidebarContent).items.length === 0}
	<SidebarLink
		href={createHref(pathname!, hash)}
		thisPage={thisPage(pathname!)}
		{icon}
		{topLevel}
		bind:isActiveChild={hasActiveChild}
	>
		{name}
	</SidebarLink>
{:else}
	<SidebarFolder
		content={{
			...content,
			pathname: pathname || ''
		} as SidebarContent}
		{topLevel}
		bind:hasActiveChild
	/>
{/if} -->
