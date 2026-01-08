<script lang="ts">
	import { getContext, onMount, type Snippet } from 'svelte';
	import type { Writable } from 'svelte/store';
	// import { page } from '$app/state';
	// import { initScrollspy } from '$lib/userInterface';
	import {
		// afterNavigate,
		// beforeNavigate,
		goto
		// pushState
		// pushState,
		// replaceState
	} from '$app/navigation';
	import type { Attachment } from 'svelte/attachments';
	// import { SvelteURL } from 'svelte/reactivity';

	let {
		href,
		thisPage,
		icon,
		topLevel = false,
		children
	}: {
		href: string;
		thisPage: boolean;
		icon: string;
		topLevel?: boolean;
		children: Snippet;
	} = $props();

	// Get context at top level during component initialization
	const scrollObserverContext = getContext<{
		observer: IntersectionObserver | undefined;
		activeSection: Writable<string | undefined>;
	}>('scrollObserver');

	// Extract element ID from href for comparison
	const elementId = $derived(href.startsWith('#') ? href.substring(1) : null);

	// Subscribe to active section to know when this link should be styled as active
	const activeSection = scrollObserverContext?.activeSection;
	const isActive = $derived(elementId && $activeSection === elementId);

	const addElementToObserver: Attachment = () => {
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

{#if thisPage}
	<!-- {@attach toggleScrollspyOnParent} -->
	<li>
		<a
			{@attach addElementToObserver}
			{href}
			class="text-base-content/80 group flex items-center gap-x-2 hover:opacity-100 {isActive
				? 'italic'
				: ''}"
		>
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
				<!-- <span
					class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
				></span> -->
				<span class="{isActive ? 'icon-[tabler--hand-finger-right]' : icon} size-5"></span>
			{/if}
			<span class="overlay-minified:hidden">{@render children?.()}</span>
		</a>
	</li>
{:else}
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
{/if}

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
