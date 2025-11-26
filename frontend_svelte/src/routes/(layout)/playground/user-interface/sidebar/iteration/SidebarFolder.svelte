<script lang="ts">
	import { type Snippet } from 'svelte';
	import type { SidebarContentItem, SidebarFolderContent } from '$lib/types';
	import { initCollapse } from '$lib/userInterface';
	import type { Attachment } from 'svelte/attachments';
	import SidebarLink from './SidebarLink.svelte';
	import SidebarFolder from './SidebarFolder.svelte';
	// change import to receiving SidebarFolderContent
	let {
		content,
		children,
		thisPage,
		createHref,
		toggleCollapse
	}: {
		content: SidebarFolderContent;
		children: Snippet;
		thisPage: (pathname: string) => boolean;
		createHref: (destinationPathname: string, hash?: string) => string;
		toggleCollapse: Attachment<HTMLElement>;
	} = $props();

	let { id, , hash, icon, items }: SidebarFolderContent = $derived(content);
</script>

<!-- TBD: this can be recursive: SidebarFolder -->
<li data-scrollspy-group="" class="space-y-0.5">
	<a
		class="collapse-toggle {thisPage(pathname)
			? 'open'
			: ''} collapse-open:bg-base-content/10 scrollspy-active:italic group"
		id={id + '-control'}
		data-collapse={'#' + id + '-collapse'}
		data-pathname={pathname}
		href={createHref(pathname, hash)}
		{@attach initCollapse}
		{@attach toggleCollapse}
	>
		<span
			class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
		></span>
		<span class="{icon} size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"></span>
		{@render children()}
		<span
			class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
		></span>
	</a>
	<ul
		id={id + '-collapse'}
		class="collapse {thisPage(pathname)
			? 'open'
			: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
		aria-labelledby={id + '-control'}
	>
		{#each items as item (item.id)}
			{#if Object.keys(item).includes('items') === false || (item as SidebarFolderContent).items.length === 0}
				<SidebarLink
					href={createHref(item.pathname || pathname, item.hash)}
					thisPage={thisPage(item.pathname || pathname)}
					icon={item.icon}
				>
					{item.name}
				</SidebarLink>
			{:else}
				<SidebarFolder
					content={item as SidebarFolderContent}
					{thisPage}
					{createHref}
					{toggleCollapse}
				>
					{content.name}
				</SidebarFolder>
			{/if}
		{/each}
	</ul>
</li>
