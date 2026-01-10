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
		hasActiveChild
	}: {
		content: SidebarFolderContent;
		topLevel?: boolean;
		hasActiveChild?: boolean;
	} = $props();
	let { id, name, pathname, hash, icon, items } = $derived({ ...content });

	// console.log("=== SidebarFolder.svelte - topoffset ===");
	// console.log(topoffset);

	const thisPage = $derived.by(() => (pathname: string) => pathname === page.url.pathname);
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
	console.log('=== SidebarFolder.svelte - hasActiveChild ===');
	console.log(hasActiveChild);

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

	const toggleCollapse: Attachment<HTMLElement> = (node: HTMLElement) => {
		// if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
		// if (page.url.pathname === node.dataset.pathname) {
		if (pathname === page.url.pathname) {
			const { element } = window.HSCollapse.getInstance(node, true);
			element.show();
		}
	};

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
	>
		<!-- data-pathname={pathname} -->
		<!-- {`[--scrollspy-offset:${topoffset}]`.toString()} -->
		<!-- max-sm:[--scrollspy-offset:56px] -->
		<!-- {`[--scrollspy-offset:${topoffset}]`.toString()} -->
		<!-- {topoffset} -->
		<!-- add [--scrollspy-offset:86] here conditionally with number being navbarBottom variable from layout. -->
		{#each items as item (item.id)}
			<SidebarItem
				content={{
					...item,
					pathname: item.pathname || pathname
				} as SidebarFolderContent}
			/>
			<!-- {scrollspyParent} -->
		{/each}
	</ul>
{/snippet}

<!-- {#if topLevel || (pathname && pathname !== page.url.pathname)}
	<li class="space-y-0.5">
		<button
			type="button"
			class="collapse-toggle {thisPage(pathname!) ? 'open' : ''} collapse-open:bg-base-content/10"
			id={id + '-control'}
			data-collapse={'#' + id + '-collapse'}
			{@attach initCollapse}
			{@attach toggleCollapse}
		>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">{name}</span>
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
		{@render collapseList()}
	</li>
{:else} -->
<li class="space-y-0.5">
	<a {href} {@attach addElementToObserver}>
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
			type="button"
			class="btn btn-circle btn-xs btn-gradient btn-base-300 collapse-toggle {thisPage(pathname!)
				? 'open'
				: ''}"
			id={id + '-control'}
			data-collapse={'#' + id + '-collapse'}
			aria-label="Toggle folder collapse"
			onclick={(e) => {
				e.preventDefault();
				e.stopPropagation();
			}}
			{@attach initCollapse}
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
		<!-- <span
				class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
			></span> -->
	</a>
	{@render collapseList()}
</li>
<!-- {/if} -->
