<script lang="ts">
	import type { SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import { initCollapse } from '$lib/userInterface';
	import type { Attachment } from 'svelte/attachments';
	// import { beforeNavigate, goto } from '$app/navigation';
	import SidebarItem from './SidebarItem.svelte';
	let {
		content,
		topLevel = false
		// scrollspyParent
	}: {
		content: SidebarFolderContent;
		topLevel?: boolean;
		// scrollspyParent: HTMLDivElement;
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

{#snippet collapseList()}
	<ul
		id={id + '-collapse'}
		class="collapse {thisPage(pathname!)
			? 'open'
			: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
		aria-labelledby={id + '-control'}
		data-pathname={pathname}
	>
		{#each items as item (item.id)}
			<SidebarItem
				content={{
					...item,
					pathname: item.pathname || pathname
				} as SidebarFolderContent}
			/>
		{/each}
	</ul>
{/snippet}

{#if topLevel || (pathname && pathname !== page.url.pathname)}
	<li class="space-y-0.5">
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
					: ''} hidden size-4 transition-all duration-300"
				role="button"
				tabindex="0"
				onclick={() => openSidebar()}
				onkeydown={() => openSidebar()}
			></span>
		</button>
		{@render collapseList()}
	</li>
{:else}
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
		{@render collapseList()}
	</li>
{/if}
