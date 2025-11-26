<script lang="ts">
	import type { SidebarContent, SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import { afterNavigate, beforeNavigate } from '$app/navigation';
	import { onMount, tick } from 'svelte';
	import type { Attachment } from 'svelte/attachments';
	import { initCollapse, initScrollspy } from '$lib/userInterface';
	import SidebarLink from './SidebarLink.svelte';
	import SidebarFolder from './SidebarFolder.svelte';

	let {
		contentList,
		scrollspyParent
	}: { contentList: SidebarContent[]; scrollspyParent: HTMLDivElement } = $props();

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

	const toggleScrollspy: Attachment<HTMLElement> = (node: HTMLElement) => {
		const addScrollspy = async (node: HTMLElement) => {
			node.setAttribute('data-scrollspy', '#scrollspy');
			node.setAttribute('data-scrollspy-scrollable-parent', '#scrollspy-scrollable-parent');
			await tick();
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

		afterNavigate(async () => {
			if (thisPage(node.dataset.pathname || '')) {
				await addScrollspy(node);
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
	const thisPage = $derived.by(() => (pathname: string) => pathname === page.url.pathname);

	const createHref = $derived.by(() => (destinationPathname: string, hash?: string) => {
		let href = '';
		if (!hash) href = destinationPathname;
		else if (thisPage(destinationPathname)) href = hash;
		else href = `${destinationPathname}${hash}`;
		return href;
	});

	onMount(() => {
		scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
		if (page.url.hash) {
			const target = document.getElementById(page.url.hash.substring(1));
			// TBD: consider opening a potential collapsed parent sections here
			if (target) {
				const parentRect = scrollspyParent!.getBoundingClientRect();
				const targetRect = target.getBoundingClientRect();

				const targetScrollTop = scrollspyParent!.scrollTop + targetRect.top - parentRect.top;
				scrollspyParent!.scrollTop = targetScrollTop;
				scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
			}
		}
	});

	const openSidebar = () => {
		const { element } = window.HSOverlay.getInstance('#collapsible-mini-sidebar', true);
		element.open();
		window.HSStaticMethods.autoInit();
	};

	const toggleCollapse: Attachment<HTMLElement> = (node: HTMLElement) => {
		if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
			const { element } = window.HSCollapse.getInstance(node, true);
			element.show();
		}
	};
</script>

{#each contentList as navItem (navItem.id)}
	{#if navItem.children.length === 0}
		<li>
			<a href={navItem.pathname}>
				<span class="{navItem.icon} size-5"></span>
				<span class="overlay-minified:hidden">{navItem.name}</span>
			</a>
		</li>
	{:else}
		<li class="space-y-0.5">
			<button
				type="button"
				class="collapse-toggle {thisPage(navItem.pathname)
					? 'open'
					: ''} collapse-open:bg-base-content/10"
				id={navItem.id + '-control'}
				data-collapse={'#' + navItem.id + '-collapse'}
				data-pathname={navItem.pathname}
				{@attach initCollapse}
				{@attach toggleCollapse}
			>
				<span class="{navItem.icon} size-5"></span>
				<span class="overlay-minified:hidden">{navItem.name}</span>
				<span
					class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:hidden size-4 transition-all duration-300"
				></span>
				<span
					class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:block overlay-minified:rotate-270 hidden size-4 transition-all duration-300"
					role="button"
					tabindex="0"
					onclick={() => openSidebar()}
					onkeydown={() => openSidebar()}
				></span>
			</button>
			<ul
				id={navItem.id + '-collapse'}
				class="collapse {thisPage(navItem.pathname)
					? 'open'
					: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
				aria-labelledby={navItem.id + '-control'}
				data-pathname={navItem.pathname}
				{@attach toggleScrollspy}
			>
				{#each navItem.children as child (child.id)}
					{#if Object.keys(child).includes('children') === false}
						<SidebarLink
							href={createHref(child.pathname || navItem.pathname, child.hash)}
							thisPage={thisPage(child.pathname || navItem.pathname)}
							icon={child.icon}
						>
							{child.name}
						</SidebarLink>
					{:else}
						<SidebarFolder
							id={child.id}
							pathname={child.pathname || navItem.pathname}
							icon={child.icon}
							name={child.name}
							children={(child as SidebarFolderContent).children}
							{thisPage}
							{createHref}
							{toggleCollapse}
						/>
					{/if}
				{/each}
			</ul>
		</li>
	{/if}
{/each}
