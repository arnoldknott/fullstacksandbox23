<script lang="ts">
	import type { Snippet } from 'svelte';
	let {
		href,
		thisPage,
		icon,
		toplevel = false,
		children
	}: {
		href: string;
		thisPage: boolean;
		icon: string;
		toplevel?: boolean;
		children: Snippet;
	} = $props();
</script>

<li>
	<a
		{href}
		class="text-base-content/80 flex items-center gap-x-2 hover:opacity-100 {thisPage
			? 'group scrollspy-active:italic'
			: ''}"
	>
		<span
			class={thisPage && !toplevel
				? 'icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline'
				: 'hidden'}
		></span>

		<span
			class="{icon} size-5 {thisPage && !toplevel
				? 'group-[.active]:hidden group-[.scrollspy-active]:hidden'
				: ''}"
		></span>
		<span class="overlay-minified:hidden">{@render children?.()}</span>
	</a>
</li>
