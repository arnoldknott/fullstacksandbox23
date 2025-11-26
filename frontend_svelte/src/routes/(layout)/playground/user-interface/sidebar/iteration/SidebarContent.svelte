<script lang="ts">
	import type { SidebarContent, SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import { afterNavigate, beforeNavigate } from '$app/navigation';
	import { tick } from 'svelte';
	import type { Attachment } from 'svelte/attachments';
	import { initCollapse, initScrollspy } from '$lib/userInterface';
	import SidebarLink from './SidebarLink.svelte';

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

{#snippet sidebarFolder(content: SidebarFolderContent)}
	{@const { id, name, pathname, hash, icon, items } = content}

	<li data-scrollspy-group="" class="space-y-0.5">
		<a
			class="collapse-toggle {thisPage(pathname!)
				? 'open'
				: ''} collapse-open:bg-base-content/10 scrollspy-active:italic group"
			id={id + '-control'}
			data-collapse={'#' + id + '-collapse'}
			data-pathname={pathname}
			href={createHref(pathname!, hash)}
			{@attach initCollapse}
			{@attach toggleCollapse}
		>
			<span
				class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
			></span>
			<span class="{icon} size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"></span>
			{name}
			<span
				class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
			></span>
		</a>
		<ul
			id={id + '-collapse'}
			class="collapse {thisPage(pathname!)
				? 'open'
				: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
			aria-labelledby={id + '-control'}
		>
			{#each items as item (item.id)}
				{#if Object.keys(item).includes('items') === false || (item as SidebarFolderContent).items.length === 0}
					<SidebarLink
						href={createHref(item.pathname || pathname!, item.hash)}
						thisPage={thisPage(item.pathname || pathname!)}
						icon={item.icon}
					>
						{item.name}
					</SidebarLink>
				{:else}
					{@render sidebarFolder({
						...item,
						pathname: item.pathname || pathname
					} as SidebarFolderContent)}
				{/if}
			{/each}
		</ul>
	</li>
{/snippet}

{#each contentList as mainItem (mainItem.id)}
	{#if mainItem.items.length === 0}
		<li>
			<a href={mainItem.pathname}>
				<span class="{mainItem.icon} size-5"></span>
				<span class="overlay-minified:hidden">{mainItem.name}</span>
			</a>
		</li>
	{:else}
		<li class="space-y-0.5">
			<button
				type="button"
				class="collapse-toggle {thisPage(mainItem.pathname)
					? 'open'
					: ''} collapse-open:bg-base-content/10"
				id={mainItem.id + '-control'}
				data-collapse={'#' + mainItem.id + '-collapse'}
				data-pathname={mainItem.pathname}
				{@attach initCollapse}
				{@attach toggleCollapse}
			>
				<span class="{mainItem.icon} size-5"></span>
				<span class="overlay-minified:hidden">{mainItem.name}</span>
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
				id={mainItem.id + '-collapse'}
				class="collapse {thisPage(mainItem.pathname)
					? 'open'
					: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
				aria-labelledby={mainItem.id + '-control'}
				data-pathname={mainItem.pathname}
				{@attach toggleScrollspy}
			>
				{#each mainItem.items as item (item.id)}
					{#if Object.keys(item).includes('items') === false || (item as SidebarFolderContent).items.length === 0}
						<SidebarLink
							href={createHref(item.pathname || mainItem.pathname, item.hash)}
							thisPage={thisPage(item.pathname || mainItem.pathname)}
							icon={item.icon}
						>
							{item.name}
						</SidebarLink>
					{:else}
						{@render sidebarFolder({
							...item,
							pathname: item.pathname || mainItem.pathname
						} as SidebarFolderContent)}
					{/if}
				{/each}
			</ul>
		</li>
	{/if}
{/each}
