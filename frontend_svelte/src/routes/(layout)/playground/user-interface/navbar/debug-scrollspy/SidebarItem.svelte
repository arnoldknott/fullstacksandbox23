<script lang="ts">
	import type { SidebarItemContent, SidebarFolderContent } from '$lib/types';
	import { page } from '$app/state';
	import SidebarFolder from './SidebarFolder.svelte';
	import SidebarLink from './SidebarLink.svelte';
	let {
		content,
		topLevel = false,
		// TBD: remove topoffset
		topoffset
		// scrollspyParent
	}: {
		content: SidebarItemContent;
		topLevel?: boolean;
		topoffset: number;
		// scrollspyParent: HTMLElement;
	} = $props();
	let { name, pathname, hash, icon } = $derived({ ...content });

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
{#if Object.keys(content).includes('items') === false || (content as SidebarFolderContent).items.length === 0}
	<!-- It's a Link -->
	<!-- {@debug content} -->
	<SidebarLink href={createHref(pathname!, hash)} thisPage={thisPage(pathname!)} {icon} {topLevel}>
		<!-- {scrollspyParent} -->
		{name}, {topoffset}
	</SidebarLink>
{:else}
	<!-- It's a Folder -->
	<SidebarFolder
		content={{
			...content,
			pathname: pathname || ''
		} as SidebarFolderContent}
		{topLevel}
		{topoffset}
	/>
	<!-- {scrollspyParent} -->
{/if}
