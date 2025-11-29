<script lang="ts">
	import type { SidebarContent, SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import { afterNavigate, beforeNavigate, goto } from '$app/navigation';
	import type { Attachment } from 'svelte/attachments';
	import { initCollapse, initScrollspy } from '$lib/userInterface';
	import SidebarLink from './SidebarLink.svelte';
	import SidebarFolder from './SidebarFolder.svelte';
	import SidebarItem from './SidebarItem.svelte';

	let {
		contentList,
		scrollspyParent
	}: { contentList: SidebarContent[]; scrollspyParent: HTMLDivElement } = $props();

	// let sidebarList: HTMLUListElement | null = $state(null);

	const forceScrolling = () => {
		if (scrollspyParent) {
			const original = scrollspyParent.scrollTop;
			// scrolls to the other end of the scroll area and back to force scrollspy to recalculate positions
			const alt =
				original < 2 ? scrollspyParent.scrollHeight : original - scrollspyParent.scrollHeight;
			scrollspyParent.scrollTop = alt;
			scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
			requestAnimationFrame(() => {
				scrollspyParent!.scrollTop = original;
				scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
			});
		}
	};

	// const addScrollspy = (node: HTMLElement) => {
	// 	node.setAttribute('data-scrollspy', '#scrollspy');
	// 	node.setAttribute('data-scrollspy-scrollable-parent', '#scrollspy-scrollable-parent');
	// 	// await tick();
	// 	initScrollspy(node);
	// 	forceScrolling();
	// };

	// $effect(() => {
	// 	let scrollspy = document.getElementById('scrollspy') as HTMLDivElement;
	// 	if (scrollspy) {
	// 		initScrollspy(sidebarList!);
	// 		forceScrolling();
	// 	}
	// });

	const addScrollspy = (node: HTMLElement) => {
		// console.log('=== addScrollspy - node ===');
		// console.log(node);
		node.setAttribute('data-scrollspy', '#scrollspy');
		node.setAttribute('data-scrollspy-scrollable-parent', '#scrollspy-scrollable-parent');
		initScrollspy(node);
		forceScrolling();
	};

	const removeScrollspy = (node: HTMLElement) => {
		node.removeAttribute('data-scrollspy');
		node.removeAttribute('data-scrollspy-scrollable-parent');
		try {
			const { element } = window.HSScrollspy.getInstance(node, true);
			element.destroy();
			/* eslint-disable no-empty */
		} catch {}
	};

	const thisPage = $derived.by(() => (pathname: string) => pathname === page.url.pathname);
	const createHref = $derived.by(() => (destinationPathname: string, hash?: string) => {
		let href = '';
		if (!hash) href = destinationPathname;
		else if (thisPage(destinationPathname)) href = hash;
		else href = `${destinationPathname}${hash}`;
		return href;
	});

	const toggleScrollspy: Attachment<HTMLElement> = (node: HTMLElement) => {
		afterNavigate(() => {
			if (thisPage(node.dataset.pathname || '')) {
				addScrollspy(node);
			}
		});

		beforeNavigate((navigator) => {
			if (!(navigator.to?.url.pathname === node.dataset.pathname)) {
				removeScrollspy(node);
			}
		});

		// Cleanup when the attachment is removed
		return async () => {
			removeScrollspy(node);
		};
	};

	// // toggleScrollspyOnParent(event.target as HTMLElement);
	// const toggleScrollspyOnParent = (node: HTMLElement) => {
	// 	const parent = node.parentElement?.parentElement?.parentElement as HTMLElement;
	// 	console.log('=== toggleScrollspyOnParent ===');
	// 	console.log(parent);
	// 	if (!parent) return;
	// 	// afterNavigate(async () => {
	// 	// if (thisPage(node.dataset.pathname || '')) {
	// 	addScrollspy(parent);
	// 	// }
	// 	// });
	// 	// beforeNavigate((navigator) => {
	// 	// 	if (!(navigator.to?.url.pathname === node.dataset.pathname)) {
	// 	// 		removeScrollspy(parent);
	// 	// 	}
	// 	// });
	// 	// Cleanup when the attachment is removed
	// 	// return async () => {
	// 	// 	removeScrollspy(parent);
	// 	// };
	// };

	const openSidebar = () => {
		const { element } = window.HSOverlay.getInstance('#collapsible-mini-sidebar', true);
		element.open();
		window.HSStaticMethods.autoInit();
	};

	const toggleCollapse: Attachment<HTMLElement> = (node: HTMLElement) => {
		// startswith on topLevel, exact match on sub-levels
		if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
			// if (page.url.pathname === node.dataset.pathname) {
			const { element } = window.HSCollapse.getInstance(node, true);
			element.show();
		}
	};

	// const toggleCollapseFolder: Attachment<HTMLElement> = (node: HTMLElement) => {
	// 	// if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
	// 	const { element } = window.HSCollapse.getInstance(node, true);
	// 	if (page.url.pathname === node.dataset.pathname) {
	// 		element.show();
	// 	} else {
	// 		element.hide();
	// 	}
	// };
</script>

<!-- TBD: reuse the SidebarFolder component also on toplevel" -->
{#each contentList as mainItem (mainItem.id)}
	<SidebarItem
		content={{ ...mainItem, pathname: mainItem.pathname || '' } as SidebarFolderContent}
		topLevel={true}
		{scrollspyParent}
	/>
{/each}
