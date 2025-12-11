<script lang="ts">
	import type { SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import { initCollapse } from '$lib/userInterface';
	import type { Attachment } from 'svelte/attachments';
	// import { beforeNavigate, goto } from '$app/navigation';
	import SidebarItem from './SidebarItem.svelte';
	// import { goto, replaceState, pushState } from '$app/navigation';
	let {
		content,
		topLevel = false,
		// TBD: remove topoffset if scrollspy-offset is unnecessary!
		topoffset
		// scrollspyParent
	}: {
		content: SidebarFolderContent;
		topLevel?: boolean;
		topoffset: number;
		// scrollspyParent: HTMLDivElement;
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
		<!-- {`[--scrollspy-offset:${topoffset}]`.toString()} -->
		<!-- {topoffset} -->
		<!-- add [--scrollspy-offset:86] here conditionally with number being navbarBottom variable from layout. -->
		{#each items as item (item.id)}
			<SidebarItem
				content={{
					...item,
					pathname: item.pathname || pathname
				} as SidebarFolderContent}
				{topoffset}
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
			{href}
			{@attach initCollapse}
			{@attach toggleCollapse}
		>
			<!-- onclick={(event) => {
				event.preventDefault();
				// pushState(href, page.state);
				goto(href, {noScroll: true, replaceState: true, state: page.state});
			}} -->
			<!-- 
			No more smooth scrolling inside page with this one:
			onclick={(event) => {
				event.preventDefault();
				replaceState(href, page.state);
				goto(href);
			}}-->
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
