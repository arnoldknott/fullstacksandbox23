<script lang="ts">
	import type { SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import { getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { initCollapse } from '$lib/userInterface';
	import type { Attachment } from 'svelte/attachments';
	import SidebarItem from './SidebarItem.svelte';
	let {
		content,
		topLevel = false,
		hasActiveChild = $bindable(false)
	}: {
		content: SidebarFolderContent;
		topLevel?: boolean;
		hasActiveChild?: boolean;
	} = $props();
	let { id, name, pathname, hash, icon, items } = $derived({ ...content });

	// Track active state for each child (use content.items for initialization to avoid referencing derived)
	let childActiveStates: boolean[] = $state(content.items.map(() => false));

	// Aggregate children's active states and propagate up
	$effect(() => {
		hasActiveChild = childActiveStates.some((active) => active);
		// if (hasActiveChild) {
		// toggleCollapse();
		// }
	});

	// console.log("=== SidebarFolder.svelte - topoffset ===");
	// console.log(topoffset);

	// TBD: refactor to avoid duplicate code from SideBarItem
	const thisPage = $derived.by(() => (pathname: string) => pathname === page.url.pathname);
	// console.log('=== SidebarFolder.svelte - thisPage(pathname!) ===');
	// $effect(() => console.log(pathname));
	const createHref = $derived.by(() => (destinationPathname: string, hash?: string) => {
		let href = '';
		if (!hash) href = destinationPathname;
		else if (thisPage(destinationPathname)) href = hash;
		else href = `${destinationPathname}${hash}`;
		return href;
	});
	let href = $derived(createHref(pathname!, hash));

	// Get context at top level during component initialization
	const scrollObserverContext = getContext<{
		observer: IntersectionObserver | undefined;
		activeSection: Writable<string | undefined>;
		visibleSections: Writable<Set<string>>;
	}>('scrollObserver');

	// Extract element ID from href for comparison
	const elementId = $derived(href.startsWith('#') ? href.substring(1) : null);
	const activeSection = scrollObserverContext?.activeSection;
	const isActive = $derived((elementId && $activeSection === elementId) || hasActiveChild);

	// Determine opacity based on visibility
	const linkOpacity = $derived(isActive ? 'opacity-100' : 'opacity-70');

	// TBD: refactor to avoid duplicate code from SideBarLink
	const addElementToObserver: Attachment = () => {
		// console.log('=== SidebarLink.svelte - addElementToObserver - attaching ===');
		// Guard against missing observer (will be available after parent mounts)
		if (scrollObserverContext?.observer) {
			// Get the element in the content that corresponds to this link and observe it
			const id = href.startsWith('#') ? href.substring(1) : null;
			const elementToObserve = id ? document.getElementById(id) : null;

			if (elementToObserve) {
				scrollObserverContext.observer.observe(elementToObserve);
				// Cleanup: unobserve when attachment is removed
				return () => scrollObserverContext.observer?.unobserve(elementToObserve);
			}
		}
	};

	// Reference to the collapse control element for reactive updates
	let collapseControl: HTMLElement | null = $state(null);

	const toggleCollapse: Attachment<HTMLElement> = (node: HTMLElement) => {
		// collapseControl = node;
		// if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
		// if (page.url.pathname === node.dataset.pathname) {
		if (pathname === page.url.pathname || hasActiveChild) {
			const { element } = window.HSCollapse.getInstance(node, true);
			element.show();
		}
	};

	//TBD: check if this can be done by FlyonUI controls
	// Reactively open collapse when a child becomes active
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

<!-- TBD: refactor to avoid duplicate code from SideBarItem -->
<li class="space-y-0.5">
	<a
		{href}
		{@attach addElementToObserver}
		class="{isActive || hasActiveChild
			? 'text-base-content italic'
			: ' text-base-content-variant'} items-center gap-x-2 transition-opacity duration-600 hover:opacity-100 {linkOpacity}"
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
		<button
			bind:this={collapseControl}
			type="button"
			class="btn btn-circle btn-xs btn-gradient btn-base-300 collapse-toggle {thisPage(pathname!) ||
			isActive
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
	</a>
	{@render collapseList()}
</li>
