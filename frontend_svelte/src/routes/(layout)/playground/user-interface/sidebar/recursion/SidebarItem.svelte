<script lang="ts">
	import type { SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import SidebarFolder from './SidebarFolder.svelte';
	import SidebarLink from './SidebarLink.svelte';
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
</script>

<!-- Is the SidebarItem a Link or a Folder? -->
{#if items.length === 0}
	<!-- It's a Link -->
	<SidebarLink href={createHref(pathname!, hash)} thisPage={thisPage(pathname!)} {icon}>
		{name}
	</SidebarLink>
{:else}
	<!-- It's a Folder -->
	<SidebarFolder
		content={{
			...content,
			pathname: pathname || ''
		} as SidebarFolderContent}
		{topLevel}
		{scrollspyParent}
	/>
{/if}

<!--
    Inside the Link & Folder components:
    Are we on toplevel? ...
    Are we on the same page, as the link's / folder's pathname is pointing to?
    => yes: use <a> and enable scrollspy
    => no: use <button>
-->
