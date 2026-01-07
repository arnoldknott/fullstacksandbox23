<script lang="ts">
	import { type Snippet } from 'svelte';
	import { page } from '$app/state';
	import { initScrollspy } from '$lib/userInterface';
	import {
		afterNavigate,
		beforeNavigate,
		goto
		// pushState
		// pushState,
		// replaceState
	} from '$app/navigation';
	// import { SvelteURL } from 'svelte/reactivity';

	let {
		href,
		thisPage,
		icon,
		// scrollspyParent,
		topLevel = false,
		children
	}: {
		href: string;
		thisPage: boolean;
		icon: string;
		// scrollspyParent: HTMLElement;
		topLevel?: boolean;
		children: Snippet;
	} = $props();

	const forceScrolling = () => {
		// if (scrollspyParent) {
		// const original = scrollspyParent.scrollTop;
		// // scrolls to the other end of the scroll area and back to force scrollspy to recalculate positions
		// const alt =
		// 	original < 2 ? scrollspyParent.scrollHeight : original - scrollspyParent.scrollHeight;
		// scrollspyParent.scrollTop = alt;
		// scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
		// requestAnimationFrame(() => {
		// 	scrollspyParent.scrollTop = original;
		// 	scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
		// });
		// }
	};

	afterNavigate(() => {
		if (thisPage) {
			forceScrolling();
		}
	});

	const addScrollspy = (node: HTMLElement) => {
		node.setAttribute('data-scrollspy', '#scrollspy');
		// Don't set the scrollable parent to body, this is the default scroll tracking!
		// node.setAttribute('data-scrollspy-scrollable-parent', '#app-body');
		// await tick();
		initScrollspy(node);
		// forceScrolling();
	};

	const removeScrollspy = (node: HTMLElement) => {
		node.removeAttribute('data-scrollspy');
		node.removeAttribute('data-scrollspy-scrollable-parent');
		// console.log('=== SidebarLink.svelte - removeScrollspy - node ===');
		// console.log(node);
		try {
			const { element } = window.HSScrollspy.getInstance(node, true);
			element.destroy();
			/* eslint-disable no-empty */
		} catch {}
	};

	const toggleScrollspyOnParent = (node: HTMLElement) => {
		const parent = node.parentElement as HTMLUListElement;
		if (
			parent &&
			parent.dataset.pathname === page.url.pathname &&
			parent.getAttribute('data-scrollspy') !== '#scrollspy'
		) {
			// afterNavigate((_navigator) => {
			if (thisPage) {
				addScrollspy(parent);
			}
			// if (navigator.to?.url.hash !== '') {
			// 	scrollspyParent.scrollTop = 0;
			// 	scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
			// }
			// });
			beforeNavigate((_navigator) => {
				// if (!(navigator.to?.url.pathname === node.dataset.pathname)) {
				removeScrollspy(parent);
				// }
			});
		}
		// Cleanup when the attachment is removed
		return async () => {
			removeScrollspy(parent);
		};
	};
</script>

{#if thisPage}
	<li {@attach toggleScrollspyOnParent}>
		<a
			{href}
			class="text-base-content/80 flex items-center gap-x-2 hover:opacity-100 {thisPage
				? 'group scrollspy-active:italic'
				: ''}"
		>
			<!-- 			onclick={() => {
				const target = document.getElementById(href)
				if (target) {
					console.log("=== SidebarLink.svelte - onclick - before scroll ===");
					pushState(href, page.state);
					target.scrollIntoView({ behavior: 'smooth' });
					console.log("=== SidebarLink.svelte - onclick - after scroll ===");
				}
				}} -->
			<!-- onclick={(event) => {
				console.log("=== SidebarLink.svelte - onclick ===");
				event.preventDefault();
				// goto(href, {noScroll: true, replaceState: true, state: page.state});
			}}  -->
			<!-- onclick={(event) => {
				// event.preventDefault();
				goto(new SvelteURL(href), {noScroll: true, replaceState: true, state: page.state});
			}}  -->
			<!-- onclick={(event) => {
				event.preventDefault();
				// pushState(href, page.state);
				goto(href, {noScroll: true, replaceState: false, state: page.state});
			}} -->
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
			{#if topLevel}
				<span class="{icon} size-5"></span>
			{:else}
				<span
					class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
				></span>
				<span class="{icon} size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"></span>
			{/if}
			<span class="overlay-minified:hidden">{@render children?.()}</span>
		</a>
	</li>
{:else}
	<li>
		<button
			type="button"
			onclick={() => {
				goto(href);
				// pushState(href, page.state);
				// goto(href, {noScroll: true, replaceState: false, state: page.state})}
			}}
		>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">{@render children?.()}</span>
		</button>
	</li>
{/if}
