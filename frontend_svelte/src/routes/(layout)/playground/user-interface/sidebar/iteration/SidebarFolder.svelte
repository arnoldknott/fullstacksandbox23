<script lang="ts">
	import type { SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import { initCollapse } from '$lib/userInterface';
	import type { Attachment } from 'svelte/attachments';
	import { goto } from '$app/navigation';
	import SidebarLink from './SidebarLink.svelte';
	import SidebarFolder from './SidebarFolder.svelte';
	let { content, topLevel = false }: { content: SidebarFolderContent; topLevel?: boolean } =
		$props();
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
		if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
			// if (page.url.pathname === node.dataset.pathname) {
			const { element } = window.HSCollapse.getInstance(node, true);
			element.show();
		}
	};
</script>

<li data-scrollspy-group="" class="space-y-0.5">
	{#if pathname && pathname !== page.url.pathname}
		<!-- TBD: add an attach, that activates the scrollspy on the parent ul. -->
		<button type="button" onclick={() => goto(createHref(pathname!, hash))}>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">{name}</span>
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
	>
		<!-- data-pathname={pathname}
			{@attach toggleScrollspy} -->
		{#each items as item (item.id)}
			{#if Object.keys(item).includes('items') === false || (item as SidebarFolderContent).items.length > 0}
				{#if item.pathname && item.pathname !== pathname}
					<!-- TBD: add an attach, that activates the scrollspy on the parent ul. -->
					<li>
						<!-- {#await toggleScrollspyOnParent(target as HTMLElement)} -->
						<button type="button" onclick={() => goto(createHref(item.pathname!, item.hash))}>
							<span class="{item.icon} size-5"></span>
							<span class="overlay-minified:hidden">{item.name}</span>
						</button>
						<!-- {/await} -->
					</li>
				{:else}
					<SidebarLink
						href={createHref(pathname!, item.hash)}
						thisPage={thisPage(pathname!)}
						icon={item.icon}
					>
						{item.name}
					</SidebarLink>
				{/if}
			{:else}
				<SidebarFolder
					content={{
						...item,
						pathname: item.pathname || pathname
					} as SidebarFolderContent}
				/>
				<!-- {@render sidebarFolder({
						...item,
						pathname: item.pathname || pathname
					} as SidebarFolderContent)} -->
			{/if}
		{/each}
	</ul>
</li>
