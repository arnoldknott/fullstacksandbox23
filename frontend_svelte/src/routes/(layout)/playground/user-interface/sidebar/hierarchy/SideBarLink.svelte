<script lang="ts">
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';
	let {
		pathname,
		hash,
		icon,
		children
	}: { pathname: string; hash?: string; icon: string; children: Snippet } = $props();

	const thisPage = $derived(pathname === page.url.pathname);

	let href = $derived(!hash ? pathname : thisPage ? hash : `${pathname}${hash} `);
</script>

<li>
	<a
		{href}
		class="text-base-content/80 flex items-center gap-x-2 hover:opacity-100 {thisPage
			? 'group scrollspy-active:italic'
			: ''}"
	>
		<span
			class={thisPage
				? 'icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline'
				: 'hidden'}
		></span>

		<span
			class="icon-[{icon}] size-5 {thisPage
				? 'group-[.active]:hidden group-[.scrollspy-active]:hidden'
				: ''}"
		></span>
		<span class="overlay-minified:hidden">{@render children?.()}</span>
	</a>
</li>
