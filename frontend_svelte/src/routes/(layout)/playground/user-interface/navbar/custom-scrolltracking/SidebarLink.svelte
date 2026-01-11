<script lang="ts">
	import { getContext, type Snippet } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { Attachment } from 'svelte/attachments';

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
	const linkOpacity = $derived(isActive ? 'opacity-100' : isVisible ? 'opacity-95' : 'opacity-70');

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
