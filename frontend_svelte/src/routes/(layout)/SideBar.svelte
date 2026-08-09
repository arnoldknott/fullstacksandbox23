<script lang="ts">
	import { scrollY } from 'svelte/reactivity/window';
	import { fly } from 'svelte/transition';

	import { page } from '$app/state';
	import Guard from '$components/Guard.svelte';
	import {
		getDebugSidebarLinks,
		getProtectedSidebarLinks,
		getSidebarLinks,
		page6Content
	} from '$lib/contexts/sidebar.svelte';
	import { initOverlay } from '$lib/userInterface';

	import LoginOutButton from './LoginOutButton.svelte';
	import Logo from './Logo.svelte';
	import SidebarItem from './SidebarItem.svelte';
	import SidebarToggleButton from './SideBarToggleButton.svelte';

	let {
		loggedIn,
		parentUrl,
		debug = $bindable(),
		navBarBottom
	}: {
		loggedIn: boolean;
		parentUrl: string | undefined;
		debug: boolean;
		navBarBottom: number;
	} = $props();

	const sidebarLinks = getSidebarLinks();
	const protectedSidebarLinks = getProtectedSidebarLinks();
	const debugSidebarLinks = getDebugSidebarLinks();
	const onThisPageLinks = $state(['dummy to keep button visisble']);

	let showOnThisPageLinks = $state(false);

	const page6Index = $derived(debugSidebarLinks.findIndex((item) => item.id === 'page6'));

	const toggleDebugPage6 = () => {
		if (page6Index >= 0) {
			debugSidebarLinks.splice(page6Index, 1);
		} else {
			debugSidebarLinks.push(...page6Content);
		}
	};
</script>

{#snippet sidebarPartItem(href: string, icon: string, text: string, listItemClasses?: string)}
	<li class="text-primary {listItemClasses}">
		<a {href}>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">{text}</span>
		</a>
	</li>
{/snippet}

<aside
	id="collapsible-mini-sidebar"
	class="overlay overlay-minified:w-19 overlay-open:translate-x-0 drawer drawer-start bg-base-150 border-base-content/20 start-0 top-0 hidden w-66 overflow-hidden border-e [--auto-close:sm] sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
	tabindex="-1"
	{@attach initOverlay}
>
	<div class="mx-7 flex h-24 flex-row items-center justify-between md:h-26">
		<div class="hidden sm:block">
			<SidebarToggleButton
				extraClasses="hidden sm:flex"
				overlayModifier={{ 'data-overlay-minifier': '#collapsible-mini-sidebar' }}
			/>
		</div>
		<div class="overlay-minified:hidden">
			<Logo />
		</div>
	</div>
	<div class="drawer-body px-2 pt-4">
		<ul class="menu p-0">
			<!-- <li><a href={resolve('/(layout)/playground/page2')}>Page 2 - top</a></li>
				<li><a href={resolve('/(layout)/playground/page2') + '#pg2loreum1'}>Page 2 - Lor. 1</a></li>
				<li><a href={resolve('/(layout)/playground/page2') + '#pg2loreum2'}>Page 2 - Lor. 2</a></li>
				<li><a href={resolve('/(layout)/playground/page2') + '#pg2loreum4'}>Page 2 - Lor. 4</a></li> -->
			{@render sidebarPartItem('/', 'icon-[material-symbols--home-outline-rounded]', 'Home')}
			{@render sidebarPartItem('/docs', 'icon-[oui--documentation]', 'Docs', 'md:hidden')}
			{@render sidebarPartItem(
				'/playground',
				'icon-[mdi--playground-seesaw]',
				'Playground',
				'md:hidden'
			)}
			<Guard>
				<!-- <hr class="border-outline -mx-2 my-3" /> -->
				{@render sidebarPartItem(
					'/dashboard',
					'icon-[material-symbols--dashboard-outline-rounded]',
					'Dashboard',
					'md:hidden'
				)}
			</Guard>
			<!-- {@render sidebarPartItem(
					'/features',
					'icon-[mdi--feature-highlight]',
					'Features',
					'md:hidden'
				)}
				{@render sidebarPartItem('/apps', 'icon-[tabler--apps]', 'Apps', 'md:hidden')}
				{@render sidebarPartItem(
					'/construction',
					'icon-[maki--construction]',
					'Construction',
					'md:hidden'
				)} -->
			<li>
				<div class="items-center sm:hidden md:ml-2">
					<LoginOutButton {loggedIn} {parentUrl} />
				</div>
			</li>
		</ul>
		<div class="divider"></div>
		<div
			class="join flex w-full flex-row rounded-full p-3 {onThisPageLinks.length === 0
				? 'pointer-events-none invisible'
				: ''}"
		>
			<button
				class="join-item btn btn-sm btn-secondary rounded-l-full {showOnThisPageLinks
					? 'btn-gradient'
					: 'btn-outline'}"
				aria-label="App navigation"
				onclick={() => (showOnThisPageLinks = !showOnThisPageLinks)}
				><span class="icon-[tabler--chevron-left] size-5"></span></button
			>
			<button
				class="join-item btn btn-sm btn-secondary grow rounded-r-full {showOnThisPageLinks
					? 'btn-outline'
					: 'btn-gradient'}"
				aria-label="On this page"
				onclick={() => (showOnThisPageLinks = !showOnThisPageLinks)}
				>On This Page <span class="icon-[tabler--chevrons-right] size-5"></span></button
			>
		</div>
		<div class="static">
			{#if !showOnThisPageLinks}
				<ul class="menu absolute p-0" transition:fly={{ x: -250, duration: 600, opacity: 0 }}>
					<!-- TBD: add a toggle between "app navigation" and "on this page" -->
					{#each sidebarLinks as sidebarItem (sidebarItem.id)}
						<!-- TBD: remove topoffset -->
						<SidebarItem
							content={{ ...sidebarItem, pathname: sidebarItem.pathname || page.url.pathname }}
							topLevel={true}
						/>
						<!-- {scrollspyParent} -->
						<!-- topoffset={navBarBottom} -->
						<!-- topoffset={internalNavigationTarget} -->
						<!-- topoffset={navBarBottom} -->
						<!-- topoffset={`[--scrollspy-offset:${navBarBottom + 8}]`} -->
					{/each}
					<Guard>
						{#each protectedSidebarLinks as protectedSidebarItem (protectedSidebarItem.id)}
							<SidebarItem
								content={{
									...protectedSidebarItem,
									pathname: protectedSidebarItem.pathname || page.url.pathname
								}}
								topLevel={true}
							/>
							<!-- {scrollspyParent} -->
							<!-- topoffset={navBarBottom} -->
						{/each}
					</Guard>
					{#if debug}
						{#each debugSidebarLinks as debugSidebarItem (debugSidebarItem.id)}
							<SidebarItem
								content={{
									...debugSidebarItem,
									pathname: debugSidebarItem.pathname || page.url.pathname
								}}
								topLevel={true}
							/>
							<!-- {scrollspyParent} -->
							<!-- topoffset={navBarBottom} -->
						{/each}
					{/if}
				</ul>
			{:else}
				<ul class="menu absolute p-0" transition:fly={{ x: 250, duration: 600, opacity: 0 }}>
					{#each debugSidebarLinks as debugSidebarItem (debugSidebarItem.id)}
						<SidebarItem
							content={{
								...debugSidebarItem,
								pathname: debugSidebarItem.pathname || page.url.pathname
							}}
							topLevel={true}
						/>
						<!-- {scrollspyParent} -->
						<!-- topoffset={navBarBottom} -->
					{/each}
				</ul>
			{/if}
		</div>
	</div>
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
		<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
	</div>

	{#if debug}
		<button
			class="btn btn-primary btn-gradient max-sm:btn-circle max-sm:ml-2 md:rounded-full"
			onclick={toggleDebugPage6}
		>
			{#if page6Index < 0}
				<span class="icon-[tabler--plus] size-5"></span>
				<div class="hidden md:block">add page 6</div>
			{:else}
				<span class="icon-[tabler--minus] size-5"></span>
				<div class="hidden md:block">remove page 6</div>
			{/if}
		</button>
		scrollY: {scrollY.current}
		<br />
		navBarBottom: {navBarBottom}
	{/if}
	<!-- {navBarBottom}
		<br />
		{locationPageAndHash?.page}{locationPageAndHash?.hash}
		<br /> -->
</aside>
