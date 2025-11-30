<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { initDropdown, initOverlay, initCollapse, initScrollspy } from '$lib/userInterface';
	import { type Snippet, tick } from 'svelte';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { Variant, type ColorConfig } from '$lib/theming';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
	import ThemePicker from '../../../components/ThemePicker.svelte';
	import ArtificialIntelligencePicker from '../../../components/ArtificialIntelligencePicker.svelte';
	import { afterNavigate, beforeNavigate } from '$app/navigation';
	import { onMount } from 'svelte';
	import type { Attachment } from 'svelte/attachments';
	import SideBarLink from './SideBarLink.svelte';
	let { children }: { children: Snippet } = $props();

	let sidebarLinks = $state([
		{
			name: 'Page 1',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/hierarchy-scroll/page1'),
			icon: 'tabler--user',
			children: []
		},
		{
			name: 'Page 2',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/hierarchy-scroll/page2'),
			id: 'page2',
			children: [
				{
					name: 'Loreum 1',
					hash: '#loreum1'
				},
				{
					name: 'Loreum 2',
					hash: '#loreum2'
				},
				{
					name: 'Sub category',
					hash: '#sub-category',
					id: 'page2-sub-category',
					children: [
						{
							name: 'Loreum 3',
							hash: '#loreum3'
						},
						{
							name: 'Loreum 4',
							hash: '#loreum4'
						}
					]
				},
				{
					name: 'Loreum 5',
					hash: '#loreum5'
				},
				{
					name: 'Loreum 6',
					hash: '#loreum6'
				}
			]
		},
		{
			name: 'Page 3',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/hierarchy-scroll/page3'),
			id: 'page3',
			children: [
				{
					name: 'Loreum 1',
					hash: '#loreum1'
				},
				{
					name: 'Loreum 2',
					hash: '#loreum2'
				},
				{
					name: 'Loreum 2a',
					hash: '#loreum2a'
				},
				{
					name: 'Sub category',
					hash: '#sub-category',
					id: 'page3-sub-category',
					children: [
						{
							name: 'Loreum 3.1',
							hash: '#loreum3p1'
						},
						{
							name: 'Loreum 3.2',
							hash: '#loreum3p2'
						}
					]
				},
				{
					name: 'Loreum 4',
					hash: '#loreum4'
				},
				{
					name: 'Loreum 5',
					hash: '#loreum5'
				}
			]
		}
	]);

	let scrollspyParent: HTMLElement | null = $state(null);

	const forceScrolling = () => {
		if (scrollspyParent) {
			const original = scrollspyParent.scrollTop;
			// scrolls to the other end of the scroll area and back to force scrollspy to recalculate positions
			const alt =
				original < 2 ? scrollspyParent.scrollHeight : original - scrollspyParent.scrollHeight;
			scrollspyParent.scrollTop = alt;
			scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
			requestAnimationFrame(() => {
				scrollspyParent!.scrollTop = original;
				scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
			});
		}
	};

	const toggleScrollspy: Attachment<HTMLElement> = (node: HTMLElement) => {
		const addScrollspy = async (node: HTMLElement) => {
			node.setAttribute('data-scrollspy', '#scrollspy');
			node.setAttribute('data-scrollspy-scrollable-parent', '#scrollspy-scrollable-parent');
			await tick();
			initScrollspy(node);
			forceScrolling();
		};

		const removeScrollspy = (node: HTMLElement) => {
			node.removeAttribute('data-scrollspy');
			node.removeAttribute('data-scrollspy-scrollable-parent');
			try {
				const { element } = window.HSScrollspy.getInstance(node, true);
				element.destroy();
				/* eslint-disable no-empty */
			} catch {}
		};

		afterNavigate(async () => {
			if (thisPage(node.dataset.pathname || '')) {
				await addScrollspy(node);
			}
		});

		beforeNavigate((navigator) => {
			if (!(navigator.to?.url.pathname === node.dataset.pathname)) {
				removeScrollspy(node);
			}
		});

		// Cleanup when the attachment is removed
		return async () => {
			removeScrollspy(node);
		};
	};
	const thisPage = $derived.by(() => (pathname: string) => pathname === page.url.pathname);

	const createHref = $derived.by(() => (destinationPathname: string, hash?: string) => {
		let href = '';
		if (!hash) href = destinationPathname;
		else if (thisPage(destinationPathname)) href = hash;
		else href = `${destinationPathname}${hash}`;
		return href;
	});

	onMount(() => {
		scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
		if (page.url.hash) {
			const target = document.getElementById(page.url.hash.substring(1));
			// TBD: consider opening a potential collapsed parent sections here
			if (target) {
				const parentRect = scrollspyParent!.getBoundingClientRect();
				const targetRect = target.getBoundingClientRect();

				const targetScrollTop = scrollspyParent!.scrollTop + targetRect.top - parentRect.top;
				scrollspyParent!.scrollTop = targetScrollTop;
				scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
			}
		}
	});

	const openSidebar = () => {
		const { element } = window.HSOverlay.getInstance('#collapsible-mini-sidebar', true);
		element.open();
		window.HSStaticMethods.autoInit();
	};

	let themeConfiguration: ColorConfig = $state({
		sourceColor: '#941ff4', // <= That's a good color!// '#353c6e' // '#769CDF',
		variant: Variant.TONAL_SPOT, // Variant.FIDELITY,//
		contrast: 0.0
	});
	let themeForm = $state<HTMLFormElement | null>(null);

	let artificialIntelligenceConfiguration: ArtificialIntelligenceConfig = $state({
		enabled: true,
		model: Model.MODEL1,
		temperature: 0.7
		// max_tokens: 2048
	});

	const toggleCollapse: Attachment<HTMLElement> = (node: HTMLElement) => {
		if (page.url.pathname.startsWith(node.dataset.pathname || '')) {
			const { element } = window.HSCollapse.getInstance(node, true);
			element.show();
		}
		// return () => {
		// 	const { element } = window.HSCollapse.getInstance(node, true);
		// 	element.hide();
		// };
	};

	let artificialIntelligenceForm = $state<HTMLFormElement | null>(null);

	const saveProfileAccount = async () => {
		console.log('=== sidebar - segmenting - saveProfileAccount - themeConfiguration ===');
		console.log($state.snapshot(themeConfiguration));
		console.log(
			'=== sidebar - segmenting - saveProfileAccount - artificialIntelligenceConfiguration ==='
		);
		console.log($state.snapshot(artificialIntelligenceConfiguration));
	};

	const updateProfileAccount: SubmitFunction = async () => {
		// console.log('=== layout - updateProfileAccount - formData ===');
		// console.log(formData);

		// Prevents page from updating/reloading:
		return () => {};
	};

	// for theme picker:
	let mode: 'light' | 'dark' = $state('dark');
</script>

{#snippet sidebarToggleButton(classes: string, overlayModifier: object)}
	<button
		type="button"
		class="btn btn-square btn-sm btn-outline btn-primary {classes}"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="collapsible-mini-sidebar"
		aria-label="Toggle Sidebar"
		{...overlayModifier}
	>
		<span
			class="icon-[material-symbols--menu-open-rounded] overlay-minified:hidden flex size-6 max-sm:hidden"
		></span>
		<span class="icon-[material-symbols--menu] overlay-minified:flex hidden size-6 max-sm:flex"
		></span>
	</button>
{/snippet}

{#snippet navbarPartItem(href: string, icon: string, text: string, textClasses?: string)}
	<li class="text-primary hidden items-center md:flex">
		<a {href} aria-label={text} class="flex items-center gap-1"
			><span class="icon-[{icon}] size-6"></span>
			<span class={textClasses}>{text}</span>
		</a>
	</li>
{/snippet}

{#snippet sidebarPartItem(href: string, icon: string, text: string, listItemClasses?: string)}
	<li class="text-primary {listItemClasses}">
		<a {href}>
			<span class="icon-[{icon}] size-5"></span>
			<span class="overlay-minified:hidden">{text}</span>
		</a>
	</li>
{/snippet}

<nav
	class="navbar rounded-box bg-base-100 shadow-shadow border-outline-variant relative sticky start-0 top-0 z-1 justify-between border-b shadow-sm md:flex md:items-center"
>
	<div class="navbar-start">
		<ul class="menu menu-horizontal ml-4 flex flex-nowrap items-center">
			{@render sidebarToggleButton('hidden sm:flex', {
				'data-overlay-minifier': '#collapsible-mini-sidebar'
			})}
			{@render sidebarToggleButton('sm:hidden', {
				'data-overlay': '#collapsible-mini-sidebar'
			})}
			<!-- {@render navbarPartItem('/features', 'mdi--feature-highlight', 'Features')}
			{@render navbarPartItem('/apps', 'tabler--apps', 'Apps')}
			{@render navbarPartItem(
				'/construction',
				'maki--construction',
				'Construction',
				'hidden lg:block'
			)} -->
			{@render navbarPartItem(
				'/playground/user-interface/sidebar/hierarchy-scroll',
				'streamline--hierarchy-2',
				'Hierarchy'
			)}
			<!-- {@render navbarPartItem(
				'/playground/user-interface/sidebar/iteration',
				'tabler--arrow-iteration',
				'Iteration'
			)} -->
		</ul>
	</div>
	<div class="navbar-center flex flex-row max-sm:scale-50">
		<div class="flex flex-col justify-center">
			<div class="title-small text-primary italic" style="line-height: 1;">Fullstack</div>
			<div class="title-small text-secondary font-bold tracking-wide" style="line-height: 1">
				Platform
			</div>
		</div>
		<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
	</div>
	<div class="navbar-end">
		<button
			class="btn btn-sm btn-text btn-circle text-primary size-8.5 md:hidden"
			aria-label="Search"
		>
			<span class="icon-[tabler--search] size-5.5"></span>
		</button>
		<div class="input mx-2 max-w-56 rounded-full max-md:hidden">
			<span class="icon-[tabler--search] text-base-content/80 my-auto me-3 size-5 shrink-0"></span>
			<label class="sr-only" for="searchInput">Search</label>
			<input type="search" class="grow" placeholder="Search" id="searchInput" />
		</div>
		<div
			class="dropdown flex items-center [--auto-close:inside] rtl:[--placement:bottom-end]"
			{@attach initDropdown}
		>
			<span
				id="dropdown-menu-icon-user"
				class="dropdown-toggle icon-[fa6-solid--user] size-6"
				role="button"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="User Menu"
			></span>
			<ul
				class="dropdown-menu bg-base-200 text-secondary shadow-outline dropdown-open:opacity-100 hidden shadow-md"
				role="menu"
				aria-orientation="vertical"
				aria-labelledby="dropdown-menu-icon-user"
			>
				<ArtificialIntelligencePicker
					{updateProfileAccount}
					{saveProfileAccount}
					bind:artificialIntelligenceForm
					bind:artificialIntelligenceConfiguration
				/>
				<li>
					<hr class="border-outline -mx-2 my-5" />
				</li>
				<ThemePicker
					{updateProfileAccount}
					{saveProfileAccount}
					bind:themeForm
					bind:mode
					bind:themeConfiguration
				/>
				<li>
					<hr class="border-outline -mx-2 my-5" />
				</li>
				<li class="flex items-center gap-2">
					<span class="icon-[tabler--settings] size-6"></span>
					<span class="grow"> Settings</span>
				</li>
			</ul>
		</div>
		<div class="flex items-center md:ml-2">
			<button
				class="btn btn-primary btn-outline shadow-primary ml-2 rounded-full shadow-sm"
				aria-label="LogInOut"
			>
				<a href="#top">LogInOut</a>
			</button>
		</div>
	</div>
</nav>

<div
	id="scrollspy-scrollable-parent"
	class="grid h-screen overflow-y-auto"
	bind:this={scrollspyParent}
>
	<aside
		id="collapsible-mini-sidebar"
		class="overlay overlay-minified:w-19 overlay-open:translate-x-0 drawer drawer-start border-base-content/20 hidden w-66 border-e pt-50 [--auto-close:sm] sm:absolute sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
		tabindex="-1"
		{@attach initOverlay}
	>
		<div class="drawer-body px-2 pt-4">
			<ul class="menu p-0">
				{@render sidebarPartItem('/', 'material-symbols--home-outline-rounded', 'Home')}
				<!-- {@render sidebarPartItem('/features', 'mdi--feature-highlight', 'Features', 'md:hidden')}
				{@render sidebarPartItem('/apps', 'tabler--apps', 'Apps', 'md:hidden')}
				{@render sidebarPartItem(
					'/construction',
					'maki--construction',
					'Construction',
					'md:hidden'
				)} -->
				{@render sidebarPartItem(
					'/playground/user-interface/sidebar/hierarchy-scroll',
					'streamline--hierarchy-2',
					'Hierarchy',
					'md:hidden'
				)}
				<!-- {@render sidebarPartItem(
					'/playground/user-interface/sidebar/iteration',
					'tabler--arrow-iteration',
					'Iteration',
					'md:hidden'
				)} -->
			</ul>
			<div class="divider"></div>
			<ul class="menu p-0">
				<li>
					<a href={sidebarLinks[0].pathname}>
						<span class="icon-[tabler--user] size-5"></span>
						<span class="overlay-minified:hidden">{sidebarLinks[0].name}</span>
					</a>
				</li>
				<!-- Parameterized page 2: -->
				<li class="space-y-0.5">
					<button
						type="button"
						class="collapse-toggle {thisPage(sidebarLinks[1].pathname)
							? 'open'
							: ''} collapse-open:bg-base-content/10"
						id={sidebarLinks[1].id + '-control'}
						data-collapse={'#' + sidebarLinks[1].id + '-collapse'}
						data-pathname={sidebarLinks[1].pathname}
						{@attach initCollapse}
						{@attach toggleCollapse}
					>
						<span class="icon-[icon-park-outline--page] size-5"></span>
						<span class="overlay-minified:hidden">{sidebarLinks[1].name}</span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:hidden size-4 transition-all duration-300"
						></span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:block overlay-minified:rotate-270 hidden size-4 transition-all duration-300"
							role="button"
							tabindex="0"
							onclick={() => openSidebar()}
							onkeydown={() => openSidebar()}
						></span>
					</button>
					<ul
						id={sidebarLinks[1].id + '-collapse'}
						class="collapse {thisPage(sidebarLinks[1].pathname)
							? 'open'
							: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
						aria-labelledby={sidebarLinks[1].id + '-control'}
						data-pathname={sidebarLinks[1].pathname}
						{@attach toggleScrollspy}
					>
						<SideBarLink
							href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[0].hash)}
							thisPage={thisPage(sidebarLinks[1].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[1].children[0].name}
						</SideBarLink>
						<SideBarLink
							href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[1].hash)}
							thisPage={thisPage(sidebarLinks[1].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[1].children[1].name}
						</SideBarLink>

						<li data-scrollspy-group="" class="space-y-0.5">
							<a
								class="collapse-toggle {thisPage(sidebarLinks[1].pathname)
									? 'open'
									: ''} collapse-open:bg-base-content/10 scrollspy-active:italic group"
								id={sidebarLinks![1].children![2].id + '-control'}
								data-collapse={'#' + sidebarLinks![1].children![2].id + '-collapse'}
								data-pathname={sidebarLinks[1].pathname}
								href={createHref(sidebarLinks[1].pathname, sidebarLinks![1].children![2].hash)}
								{@attach initCollapse}
								{@attach toggleCollapse}
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[icon-park-outline--page] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								{sidebarLinks![1].children![2].name}
								<span
									class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
								></span>
							</a>
							<ul
								id={sidebarLinks![1].children![2].id + '-collapse'}
								class="collapse {thisPage(sidebarLinks[1].pathname)
									? 'open'
									: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
								aria-labelledby={sidebarLinks![1].children![2].id + '-control'}
							>
								<SideBarLink
									href={createHref(
										sidebarLinks[1].pathname,
										sidebarLinks[1].children![2].children![0].hash
									)}
									thisPage={thisPage(sidebarLinks[1].pathname)}
									icon="mdi--text"
								>
									{sidebarLinks[1].children![2].children![0].name}
								</SideBarLink>
								<SideBarLink
									href={createHref(
										sidebarLinks[1].pathname,
										sidebarLinks[1].children![2].children![1].hash
									)}
									thisPage={thisPage(sidebarLinks[1].pathname)}
									icon="mdi--text"
								>
									{sidebarLinks[1].children![2].children![1].name}
								</SideBarLink>
							</ul>
						</li>
						<SideBarLink
							href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children![3].hash)}
							thisPage={thisPage(sidebarLinks[1].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[1].children![3].name}
						</SideBarLink>
						<SideBarLink
							href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children![4].hash)}
							thisPage={thisPage(sidebarLinks[1].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[1].children![4].name}
						</SideBarLink>
					</ul>
				</li>
				<!-- Parameterized page 3: -->
				<li class="space-y-0.5">
					<button
						type="button"
						class="collapse-toggle {thisPage(sidebarLinks[2].pathname)
							? 'open'
							: ''} collapse-open:bg-base-content/10"
						id={sidebarLinks[2].id + '-control'}
						data-collapse={'#' + sidebarLinks[2].id + '-collapse'}
						data-pathname={sidebarLinks[2].pathname}
						{@attach initCollapse}
						{@attach toggleCollapse}
					>
						<span class="icon-[icon-park-outline--page] size-5"></span>
						<span class="overlay-minified:hidden">{sidebarLinks[2].name}</span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:hidden size-4 transition-all duration-300"
						></span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:block overlay-minified:rotate-270 hidden size-4 transition-all duration-300"
							role="button"
							tabindex="0"
							onclick={() => openSidebar()}
							onkeydown={() => openSidebar()}
						></span>
					</button>
					<ul
						id={sidebarLinks[2].id + '-collapse'}
						class="collapse {thisPage(sidebarLinks[2].pathname)
							? 'open'
							: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
						aria-labelledby={sidebarLinks[2].id + '-control'}
						data-pathname={sidebarLinks[2].pathname}
						{@attach toggleScrollspy}
					>
						<SideBarLink
							href={createHref(sidebarLinks[2].pathname, sidebarLinks[2].children[0].hash)}
							thisPage={thisPage(sidebarLinks[2].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[2].children[0].name}
						</SideBarLink>
						<SideBarLink
							href={createHref(sidebarLinks[2].pathname, sidebarLinks[2].children[1].hash)}
							thisPage={thisPage(sidebarLinks[2].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[2].children[1].name}
						</SideBarLink>
						<SideBarLink
							href={createHref(sidebarLinks[2].pathname, sidebarLinks[2].children[2].hash)}
							thisPage={thisPage(sidebarLinks[2].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[2].children[2].name}
						</SideBarLink>
						<li data-scrollspy-group="" class="space-y-0.5">
							<a
								class="collapse-toggle {thisPage(sidebarLinks[2].pathname)
									? 'open'
									: ''} collapse-open:bg-base-content/10 scrollspy-active:italic group"
								id={sidebarLinks![2].children![3].id + '-control'}
								data-collapse={'#' + sidebarLinks![2].children![3].id + '-collapse'}
								data-pathname={sidebarLinks[2].pathname}
								href={createHref(sidebarLinks[2].pathname, sidebarLinks![2].children![3].hash)}
								{@attach initCollapse}
								{@attach toggleCollapse}
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[icon-park-outline--page] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								{sidebarLinks![2].children![3].name}
								<span
									class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
								></span>
							</a>
							<ul
								id={sidebarLinks![2].children![3].id + '-collapse'}
								class="collapse {thisPage(sidebarLinks[2].pathname)
									? 'open'
									: 'hidden'} w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
								aria-labelledby={sidebarLinks![2].children![3].id + '-control'}
							>
								<SideBarLink
									href={createHref(
										sidebarLinks[2].pathname,
										sidebarLinks[2].children![3].children![0].hash
									)}
									thisPage={thisPage(sidebarLinks[2].pathname)}
									icon="mdi--text"
								>
									{sidebarLinks[2].children![3].children![0].name}
								</SideBarLink>
								<SideBarLink
									href={createHref(
										sidebarLinks[2].pathname,
										sidebarLinks[2].children![3].children![1].hash
									)}
									thisPage={thisPage(sidebarLinks[2].pathname)}
									icon="mdi--text"
								>
									{sidebarLinks[2].children![3].children![1].name}
								</SideBarLink>
							</ul>
						</li>
						<SideBarLink
							href={createHref(sidebarLinks[2].pathname, sidebarLinks[2].children![4].hash)}
							thisPage={thisPage(sidebarLinks[2].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[2].children![4].name}
						</SideBarLink>
						<SideBarLink
							href={createHref(sidebarLinks[2].pathname, sidebarLinks[2].children![5].hash)}
							thisPage={thisPage(sidebarLinks[2].pathname)}
							icon="mdi--text"
						>
							{sidebarLinks[2].children![5].name}
						</SideBarLink>
					</ul>
				</li>
				<li>
					<a href="./page4/">
						<span class="icon-[tabler--mail] size-5"></span>
						<span class="overlay-minified:hidden">Further Page</span>
					</a>
				</li>
				<!-- <li>
					<a href="./scrollspy/#">
						<span class="icon-[tabler--shopping-bag] size-5"></span>
						<span class="overlay-minified:hidden">About</span>
					</a>
				</li> -->
				<li>
					<button
						class="btn btn-primary btn-outline shadow-primary mt-4 w-full rounded-full shadow-sm"
						aria-label="Console log page"
						onclick={() => console.log($state.snapshot(page))}
					>
						Console log page
					</button>
				</li>
			</ul>
		</div>
	</aside>
	<div class="sm:overlay-minified:ps-19 bg-base-100 ps-64 transition-all duration-300 max-sm:ps-0">
		<div class="bg-base-100 transition-all duration-300">
			<div id="scrollspy" class="space-y-4 pe-1">
				{@render children?.()}
			</div>
		</div>
	</div>
</div>
