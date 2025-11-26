<script lang="ts">
	import type { SidebarFolderContent } from '$lib/types';
	import { initCollapse } from '$lib/userInterface';
	import type { Attachment } from 'svelte/attachments';
	let {
		id,
		pathname,
		icon,
		name,
		children,
		thisPage,
		createHref,
		toggleCollapse
	}: {
		id: string;
		pathname: string;
		icon: string;
		name: string;
		children?: SidebarFolderContent['children'];
		thisPage: (pathname: string) => boolean;
		createHref: (destinationPathname: string, hash?: string) => string;
		toggleCollapse: Attachment<HTMLElement>;
	} = $props();
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
		href={createHref(pathname)}
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
		class="collapse {thisPage(pathname)
			? 'open'
			: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
		aria-labelledby={id + '-control'}
	>
		TBD: either recursive SidebarFolder or SidebarLink here.
		<!-- depends if child has children! -->
	</ul>
</li>
