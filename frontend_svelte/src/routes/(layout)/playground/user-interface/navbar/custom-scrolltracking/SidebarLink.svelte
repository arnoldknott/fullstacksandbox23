<script lang="ts">
	import { getContext, type Snippet } from 'svelte';
	import type { Writable } from 'svelte/store';

	// import { page } from '$app/state';
	// import { initScrollspy } from '$lib/userInterface';
	// import {
	// afterNavigate,
	// beforeNavigate,
	// goto
	// pushState
	// pushState,
	// replaceState
	// } from '$app/navigation';
	import type { Attachment } from 'svelte/attachments';
	// import { SvelteURL } from 'svelte/reactivity';

	let {
		href,
		thisPage,
		icon,
		topLevel = false,
		isActiveChild = $bindable(),
		children
	}: {
		href: string;
		thisPage: boolean;
		icon: string;
		topLevel?: boolean;
		isActiveChild?: boolean;
		children: Snippet;
	} = $props();

	// Get context at top level during component initialization
	const scrollObserverContext = getContext<{
		observer: IntersectionObserver | undefined;
		activeSection: Writable<string | undefined>;
		visibleSections: Writable<Set<string>>;
	}>('scrollObserver');

	// Extract element ID from href for comparison
	const elementId = $derived(href.startsWith('#') ? href.substring(1) : null);

	// Subscribe to active section and visible sections
	const activeSection = scrollObserverContext?.activeSection;
	const visibleSections = scrollObserverContext?.visibleSections;

	const isActive = $derived(elementId && thisPage && $activeSection === elementId);
	$effect(() => {
		isActiveChild = isActive ? true : false;
	});
	const isVisible = $derived(elementId && thisPage && $visibleSections?.has(elementId));

	// Determine opacity based on visibility
	const linkOpacity = $derived(
		isActive || thisPage ? 'opacity-100' : isVisible ? 'opacity-95' : 'opacity-70'
	);

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
</script>

<!-- {#if thisPage} -->
<!-- {@attach toggleScrollspyOnParent} -->
<li>
	<a
		{@attach addElementToObserver}
		{href}
		class="{isActive || isVisible || thisPage
			? 'text-base-content italic'
			: ' text-base-content-variant'} flex items-center gap-x-2 transition-opacity duration-600 hover:opacity-100 {linkOpacity}"
	>
		<!-- data-sveltekit-noscroll={thisPage ? 'true' : undefined} -->
		<!-- 			onclick={() => {
				const target = document.getElementById(href)
				if (target) {
					console.log("=== SidebarLink.svelte - onclick - before scroll ===");
					pushState(href, page.state);
					target.scrollIntoView({ behavior: 'smooth' });
					console.log("=== SidebarLink.svelte - onclick - after scroll ===");
				}
				}} -->
		<!-- onclick={(event) => {
				console.log("=== SidebarLink.svelte - onclick ===");
				event.preventDefault();
				// goto(href, {noScroll: true, replaceState: true, state: page.state});
			}}  -->
		<!-- onclick={(event) => {
				// event.preventDefault();
				goto(new SvelteURL(href), {noScroll: true, replaceState: true, state: page.state});
			}}  -->
		<!-- onclick={(event) => {
				event.preventDefault();
				// pushState(href, page.state);
				goto(href, {noScroll: true, replaceState: false, state: page.state});
			}} -->
		<!-- onclick={(event) => {
				if (!thisPage)
				{ 
					event.preventDefault();
					pushState(href, page.state);
					goto(href)
				}
				else{
					pushState(href, page.state);
				};
			}} -->
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
		<span class="overlay-minified:hidden {isActive ? 'text-base-content/100' : ''}"
			>{@render children?.()}</span
		>
	</a>
</li>
<!-- {:else}
	<li>
		<button
			type="button"
			onclick={() => {
				goto(href);
				// pushState(href, page.state);
				// goto(href, {noScroll: true, replaceState: false, state: page.state})}
			}}
		>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">{@render children?.()}</span>
		</button>
	</li>
{/if} -->

<!-- 
Old code from scrollspy - might still be handy to register and unregister observer
const addScrollspy = (node: HTMLElement) => {
		node.setAttribute('data-scrollspy', '#scrollspy');
		// Don't set the scrollable parent to body, this is the default scroll tracking!
		// node.setAttribute('data-scrollspy-scrollable-parent', '#app-body');
		// await tick();
		initScrollspy(node);
		// forceScrolling();
	};

	const removeScrollspy = (node: HTMLElement) => {
		node.removeAttribute('data-scrollspy');
		// node.removeAttribute('data-scrollspy-scrollable-parent');
		// console.log('=== SidebarLink.svelte - removeScrollspy - node ===');
		// console.log(node);
		try {
			const { element } = window.HSScrollspy.getInstance(node, true);
			element.destroy();
			/* eslint-disable no-empty */
		} catch {}
	};

	const toggleScrollspyOnParent = (node: HTMLElement) => {
		const parent = node.parentElement as HTMLUListElement;
		if (
			parent &&
			parent.dataset.pathname === page.url.pathname &&
			parent.getAttribute('data-scrollspy') !== '#scrollspy'
		) {
			// afterNavigate((_navigator) => {
			if (thisPage) {
				console.log('=== SidebarLink.svelte - toggleScrollspyOnParent - addScrollspy ===');
				addScrollspy(parent);
			}
			// if (navigator.to?.url.hash !== '') {
			// 	scrollspyParent.scrollTop = 0;
			// 	scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
			// }
			// });
			beforeNavigate((_navigator) => {
				// if (!(navigator.to?.url.pathname === node.dataset.pathname)) {
				removeScrollspy(parent);
				// }
			});
		}
		// Cleanup when the attachment is removed
		return async () => {
			removeScrollspy(parent);
		};
	}; -->
