<script lang="ts">
	import type { SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import { initCollapse, initScrollspy } from '$lib/userInterface';
	import type { Attachment } from 'svelte/attachments';
	import { beforeNavigate, goto } from '$app/navigation';
	import SidebarLink from './SidebarLink.svelte';
	import SidebarFolder from './SidebarFolder.svelte';
	let {
		content,
		topLevel = false,
		scrollspyParent
	}: {
		content: SidebarFolderContent;
		topLevel?: boolean;
		scrollspyParent: HTMLDivElement;
	} = $props();
	let { id, name, pathname, hash, icon, items } = $derived({ ...content });

	const thisPage = $derived.by(() => (pathname: string) => pathname === page.url.pathname);
	const createHref = $derived.by(() => (destinationPathname: string, hash?: string) => {
		let href = '';
		if (!hash) href = destinationPathname;
		else if (thisPage(destinationPathname)) href = hash;
		else href = `${destinationPathname}${hash}`;
		return href;
	});

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

	const toggleScrollspyOnParent = (node: HTMLElement) => {
		const parent = node.parentElement as HTMLElement;
		// if (!parent) return;
		if (parent && parent.dataset.pathname === page.url.pathname) {
			// afterNavigate(async () => {
			// 	if (thisPage(node.dataset.pathname || '')) {
			addScrollspy(parent);
			// 	}
			// });
			beforeNavigate((navigator) => {
				if (!(navigator.to?.url.pathname === node.dataset.pathname)) {
					removeScrollspy(parent);
				}
			});
		}
		// Cleanup when the attachment is removed
		return async () => {
			removeScrollspy(parent);
		};
	};

	const toggleCollapse: Attachment<HTMLElement> = (node: HTMLElement) => {
		// if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
		if (page.url.pathname === node.dataset.pathname) {
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

<!-- TBD: declutter the recursivity -->
<li data-scrollspy-group="" class="space-y-0.5">
	{#if items.length === 0}
		<!-- Does not get used: if items.length === 0, then it's not a folder! -->
		<!-- Might get relevant though on toplevel -->
		<!-- TBD: add an attach, that activates the scrollspy on the parent ul. -->
		<button type="button" onclick={() => goto(createHref(pathname!, hash))}>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">S: {name}</span>
		</button>
	{:else if topLevel || (pathname && pathname !== page.url.pathname)}
		<button
			type="button"
			class="collapse-toggle {thisPage(pathname!) ? 'open' : ''} collapse-open:bg-base-content/10"
			id={id + '-control'}
			data-collapse={'#' + id + '-collapse'}
			data-pathname={pathname}
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
					: 'hidden '} size-4 transition-all duration-300"
				role="button"
				tabindex="0"
				onclick={() => openSidebar()}
				onkeydown={() => openSidebar()}
			></span>
		</button>
	{:else}
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
	{/if}
	<ul
		id={id + '-collapse'}
		class="collapse {thisPage(pathname!)
			? 'open'
			: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
		aria-labelledby={id + '-control'}
		data-pathname={pathname}
	>
		<!-- data-pathname={pathname}
			{@attach toggleScrollspy} -->
		{#each items as item (item.id)}
			{#if Object.keys(item).includes('items') === false || (item as SidebarFolderContent).items.length > 0}
				{#if item.pathname && item.pathname !== page.url.pathname}
					<!-- TBD: add an attach, that activates the scrollspy on the parent ul. -->
					<!-- Repeats code from above. -->
					<li>
						<!-- {#await toggleScrollspyOnParent(target as HTMLElement)} -->
						<button type="button" onclick={() => goto(createHref(item.pathname!, item.hash))}>
							<span class="{item.icon} size-5"></span>
							<span class="overlay-minified:hidden">E: {item.name}</span>
						</button>
						<!-- {/await} -->
					</li>
				{:else}
					<div {@attach toggleScrollspyOnParent}>
						<SidebarLink
							href={createHref(pathname!, item.hash)}
							thisPage={thisPage(pathname!)}
							icon={item.icon}
						>
							S: {item.name}
						</SidebarLink>
					</div>
				{/if}
			{:else}
				<SidebarFolder
					content={{
						...item,
						pathname: item.pathname || pathname
					} as SidebarFolderContent}
					{scrollspyParent}
				/>
			{/if}
		{/each}
	</ul>
</li>
