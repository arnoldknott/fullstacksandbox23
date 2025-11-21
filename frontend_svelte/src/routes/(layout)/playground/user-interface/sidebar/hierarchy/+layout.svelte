<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { initDropdown, initOverlay, initCollapse, initScrollspy } from '$lib/userInterface';
	import { type Snippet } from 'svelte';
	import { Variant, type ColorConfig } from '$lib/theming';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
	import ThemePicker from '../../../components/ThemePicker.svelte';
	import ArtificialIntelligencePicker from '../../../components/ArtificialIntelligencePicker.svelte';
	import { afterNavigate } from '$app/navigation';
	import JsonData from '$components/JsonData.svelte';
	import type { Attachment } from 'svelte/attachments';
	let { children }: { children: Snippet } = $props();

	let sidebarLinks = [
		{
			name: 'Page 1',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/hierarchy/page1'),
			children: []
		},
		{
			name: 'Page 2',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/hierarchy/page2'),
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
			pathname: resolve('/(layout)/playground/user-interface/sidebar/hierarchy/page3'),
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
		}
	];

	// console.log('=== sidebar - hierarchy - sidebarLinks ===');
	// console.log(sidebarLinks);

	// $effect(() => {
	// 	console.log('=== sidebar - hierarchy - current scrollspy ===');
	// 	console.log(`scrollspy-${page.url.pathname.split('/').at(-1)}`);
	// });

	// const activateScrollspy: Action<HTMLElement> = (node) => {
	// 	initScrollspy(node);
	// };

	// const activateScrollspy: Action<HTMLElement, string> = (node, path: string) => {
	// 	initScrollspy(node);
	// 	if (!thisPage(path)) {
	// 		node.removeAttribute('data-scrollspy');
	// 		node.removeAttribute('data-scrollspy-scrollable-parent');
	// 	} else {
	// 		node.setAttribute('data-scrollspy', '#scrollspy');
	// 		node.setAttribute('data-scrollspy-scrollable-parent', '#scrollspy-scrollable-parent');
	// 	}

	// 	return {
	// 		destroy() {
	// 			// Cleanup if necessary when the action is removed
	// 		}
	// 	};
	// };
	// // on <ul> with initScrollspy:
	// use:activateScrollspy={sidebarLinks[1].pathname}

	// afterNavigate(() => {
	// 	if (thisPage(sidebarLinks[1].pathname))
	// 		initScrollspy(document.querySelector('#page2-collapse') as HTMLElement);
	// });
	const toggleScrollspy: Attachment<HTMLElement> = (node: HTMLElement) => {
		afterNavigate(() => {
			if (!thisPage(sidebarLinks[1].pathname)) {
				node.removeAttribute('data-scrollspy');
				node.removeAttribute('data-scrollspy-scrollable-parent');
				// If scrollspy was not initialized, calling destroy will throw error
				try {
					const { element } = window.HSScrollspy.getInstance(node, true);
					element.destroy();
				} catch {}
			} else {
				node.setAttribute('data-scrollspy', '#scrollspy');
				node.setAttribute('data-scrollspy-scrollable-parent', '#scrollspy-scrollable-parent');
				initScrollspy(node);
			}
		});
		return () => {
			// Cleanup when the attachment is removed
			node.removeAttribute('data-scrollspy');
			node.removeAttribute('data-scrollspy-scrollable-parent');
			try {
				const { element } = window.HSScrollspy.getInstance(node, true);
				element.destroy();
			} catch {}
		};
	};

	const thisPage = (destinationPathename: string) => {
		return destinationPathename === page.url.pathname;
	};
	// const thisPage = $derived(destinationPathename === page.url.pathname;)

	const createHref = (destinationPathname: string, hash?: string) => {
		let href = '';
		if (!hash) href = destinationPathname;
		else if (thisPage(destinationPathname)) href = hash;
		else href = `${destinationPathname}${hash}`;
		return href;
	};

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

	let artificialIntelligenceForm = $state<HTMLFormElement | null>(null);

	const saveProfileAccount = async () => {
		console.log('=== sidebar - segmenting - saveProfileAccount - themeConfiguration ===');
		console.log($state.snapshot(themeConfiguration));
		console.log(
			'=== sidebar - segmenting - saveProfileAccount - artificialIntelligenceConfiguration ==='
		);
		console.log($state.snapshot(artificialIntelligenceConfiguration));
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
				'/playground/user-interface/sidebar/hierarchy',
				'streamline--hierarchy-2',
				'Hierarchy'
			)}
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
					{saveProfileAccount}
					bind:artificialIntelligenceForm
					bind:artificialIntelligenceConfiguration
				/>
				<li>
					<hr class="border-outline -mx-2 my-5" />
				</li>
				<ThemePicker {saveProfileAccount} bind:themeForm bind:mode bind:themeConfiguration />
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

<div id="scrollspy-scrollable-parent" class="grid h-screen overflow-y-auto">
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
					'/playground/user-interface/sidebar/hierarchy',
					'streamline--hierarchy-2',
					'Hierarchy',
					'md:hidden'
				)}
			</ul>
			<div class="divider"></div>
			<ul class="menu p-0">
				<li>
					<a href={sidebarLinks[0].pathname}>
						<span class="icon-[tabler--user] size-5"></span>
						<span class="overlay-minified:hidden">{sidebarLinks[0].name}</span>
					</a>
				</li>
				<li class="space-y-0.5">
					<button
						type="button"
						class="collapse-toggle collapse-open:bg-base-content/10"
						id="page2"
						data-collapse="#page2-collapse"
						{@attach initCollapse}
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
						id="page2-collapse"
						class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
						aria-labelledby="page2"
						{@attach toggleScrollspy}
						{@attach initScrollspy}
					>
						<li>
							<a
								href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[0].hash)}
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 hover:opacity-100"
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>

								<span
									class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								{sidebarLinks[1].children[0].name}
							</a>
						</li>
						<li>
							<a
								href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[1].hash)}
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 hover:opacity-100"
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								{sidebarLinks[1].children[1].name}
							</a>
						</li>
						<!-- <li>
							<a
								href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[0].hash)}
								class={thisPage(sidebarLinks[1].pathname)
									? 'group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2  hover:opacity-100'
									: ''}
							>
								{#if thisPage(sidebarLinks[1].pathname)}
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
								{/if}
								<span
									class="icon-[mdi--text] size-5 {thisPage(sidebarLinks[1].pathname)
										? 'group-[.active]:hidden group-[.scrollspy-active]:hidden'
										: ''}"
								></span>
								{sidebarLinks[1].children[0].name}
							</a>
						</li>
						<li>
							<a
								href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[1].hash)}
								class={thisPage(sidebarLinks[1].pathname)
									? 'group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2  hover:opacity-100'
									: ''}
							>
								{#if thisPage(sidebarLinks[1].pathname)}
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
								{/if}
								<span
									class="icon-[mdi--text] size-5 {thisPage(sidebarLinks[1].pathname)
										? 'group-[.active]:hidden group-[.scrollspy-active]:hidden'
										: ''}"
								></span>
								{sidebarLinks[1].children[1].name}
							</a>
						</li> -->
						<!-- <li data-scrollspy-group="" class="space-y-0.5">
							<a
								class="collapse-toggle collapse-open:bg-base-content/10 scrollspy-active:italic group"
								id="page2-sub-category"
								data-collapse="#page2-sub-category-collapse"
								href="#sub-category"
								{@attach initCollapse}
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[icon-park-outline--page] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								Sub category
								<span
									class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
								></span>
							</a>
							<ul
								id="page2-sub-category-collapse"
								class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
								aria-labelledby="page2-sub-category"
							>
								<li>
									<a
										href="#loreum3"
										class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
									>
										<span
											class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
										></span>
										<span
											class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
										></span>
										Loreum 3
									</a>
								</li>
								<li>
									<a
										href="#loreum4"
										class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
									>
										<span
											class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
										></span>
										<span
											class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
										></span>
										Loreum 4
									</a>
								</li>
							</ul>
						</li>
						<li>
							<a
								href="#loreum5"
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								Loreum 5
							</a>
						</li>
						<li>
							<a
								href="#loreum6"
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								Loreum 6
							</a>
						</li> -->
					</ul>
					<!-- <button
						type="button"
						class="collapse-toggle collapse-open:bg-base-content/10"
						id="page2"
						data-collapse="#page2-collapse"
						{@attach thisPage(sidebarLinks[1].pathname) ? initCollapse : undefined}
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
						id="page2-collapse"
						class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
						aria-labelledby="page2"
						data-scrollspy={thisPage(sidebarLinks[1].pathname) ? '#scrollspy' : undefined}
						data-scrollspy-scrollable-parent={thisPage(sidebarLinks[1].pathname)
							? '#scrollspy-scrollable-parent'
							: undefined}
						{@attach thisPage(sidebarLinks[1].pathname) ? initScrollspy : undefined}
					>
						<li>
							<a
								href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[0].hash)}
								class={thisPage(sidebarLinks[1].pathname)
									? 'group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100'
									: ''}
							>
								{#if thisPage(sidebarLinks[1].pathname)}
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
								{/if}
								<span
									class="icon-[mdi--text] size-5 {thisPage(sidebarLinks[1].pathname)
										? 'group-[.active]:hidden group-[.scrollspy-active]:hidden'
										: ''}"
								></span>
								{sidebarLinks[1].children[0].name}
							</a>
						</li>
						<li>
							<a
								href="#loreum2"
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								Loreum 2
							</a>
						</li>
						<li data-scrollspy-group="" class="space-y-0.5">
							<a
								class="collapse-toggle collapse-open:bg-base-content/10 scrollspy-active:italic group"
								id="page2-sub-category"
								data-collapse="#page2-sub-category-collapse"
								href="#sub-category"
								{@attach initCollapse}
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[icon-park-outline--page] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								Sub category
								<span
									class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
								></span>
							</a>
							<ul
								id="page2-sub-category-collapse"
								class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
								aria-labelledby="page2-sub-category"
							>
								<li>
									<a
										href="#loreum3"
										class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
									>
										<span
											class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
										></span>
										<span
											class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
										></span>
										Loreum 3
									</a>
								</li>
								<li>
									<a
										href="#loreum4"
										class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
									>
										<span
											class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
										></span>
										<span
											class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
										></span>
										Loreum 4
									</a>
								</li>
							</ul>
						</li>
						<li>
							<a
								href="#loreum5"
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								Loreum 5
							</a>
						</li>
						<li>
							<a
								href="#loreum6"
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								Loreum 6
							</a>
						</li>
					</ul> -->
					<!-- {#if !thisPage(sidebarLinks[1].pathname)}
						<button
							type="button"
							class="collapse-toggle collapse-open:bg-base-content/10"
							id="page2"
							data-collapse="#page2-collapse"
							{@attach initCollapse}
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
							id="page2-collapse"
							class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
							aria-labelledby="page2"
						>
							<li>
								<a href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[0].hash)}>
									<span class="icon-[mdi--text] size-5"></span>
									{sidebarLinks[1].children[0].name}
								</a>
							</li>
							<li>
								<a
									href="#loreum2"
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 2
								</a>
							</li>
							<li data-scrollspy-group="" class="space-y-0.5">
								<a
									class="collapse-toggle collapse-open:bg-base-content/10 scrollspy-active:italic group"
									id="page2-sub-category"
									data-collapse="#page2-sub-category-collapse"
									href="#sub-category"
									{@attach initCollapse}
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[icon-park-outline--page] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Sub category
									<span
										class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
									></span>
								</a>
								<ul
									id="page2-sub-category-collapse"
									class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
									aria-labelledby="page2-sub-category"
								>
									<li>
										<a
											href="#loreum3"
											class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
										>
											<span
												class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
											></span>
											<span
												class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
											></span>
											Loreum 3
										</a>
									</li>
									<li>
										<a
											href="#loreum4"
											class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
										>
											<span
												class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
											></span>
											<span
												class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
											></span>
											Loreum 4
										</a>
									</li>
								</ul>
							</li>
							<li>
								<a
									href="#loreum5"
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 5
								</a>
							</li>
							<li>
								<a
									href="#loreum6"
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 6
								</a>
							</li>
						</ul>
					{:else}
						<button
							type="button"
							class="collapse-toggle collapse-open:bg-base-content/10"
							id="page2"
							data-collapse="#page2-collapse"
							{@attach initCollapse}
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
							id="page2-collapse"
							class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
							aria-labelledby="page2"
							data-scrollspy="#scrollspy"
							data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
							{@attach initScrollspy}
						>
							<li>
								<a
									href={createHref(sidebarLinks[1].pathname, sidebarLinks[1].children[0].hash)}
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									{sidebarLinks[1].children[0].name}
								</a>
							</li>
							<li>
								<a
									href="#loreum2"
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 2
								</a>
							</li>
							<li data-scrollspy-group="" class="space-y-0.5">
								<a
									class="collapse-toggle collapse-open:bg-base-content/10 scrollspy-active:italic group"
									id="page2-sub-category"
									data-collapse="#page2-sub-category-collapse"
									href="#sub-category"
									{@attach initCollapse}
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[icon-park-outline--page] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Sub category
									<span
										class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
									></span>
								</a>
								<ul
									id="page2-sub-category-collapse"
									class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
									aria-labelledby="page2-sub-category"
								>
									<li>
										<a
											href="#loreum3"
											class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
										>
											<span
												class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
											></span>
											<span
												class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
											></span>
											Loreum 3
										</a>
									</li>
									<li>
										<a
											href="#loreum4"
											class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
										>
											<span
												class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
											></span>
											<span
												class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
											></span>
											Loreum 4
										</a>
									</li>
								</ul>
							</li>
							<li>
								<a
									href="#loreum5"
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 5
								</a>
							</li>
							<li>
								<a
									href="#loreum6"
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 6
								</a>
							</li>
						</ul>
					{/if} -->
				</li>
				<li class="space-y-0.5">
					<button
						class="collapse-toggle collapse-open:bg-base-content/10"
						id="page3"
						data-collapse="#page3-collapse"
						type="button"
						{@attach initCollapse}
					>
						<span class="icon-[tabler--apps] size-5"></span>
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
						id="page3-collapse"
						class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
						aria-labelledby="page3"
					>
						<li>
							<a href={sidebarLinks[2].pathname}>
								<span class="icon-[tabler--message] size-5"></span>
								Loreum 1
							</a>
						</li>
						<li>
							<a href="#loreum4">
								<span class="icon-[tabler--calendar] size-5"></span>
								Loreum 2
							</a>
						</li>
						<li class="space-y-0.5">
							<button
								class="collapse-toggle collapse-open:bg-base-content/10"
								id="sub-menu-academy"
								data-collapse="#sub-menu-academy-collapse"
								type="button"
								{@attach initCollapse}
							>
								<span class="icon-[tabler--book] size-5"></span>
								Academy
								<span
									class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
								></span>
							</button>
							<ul
								id="sub-menu-academy-collapse"
								class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
								aria-labelledby="sub-menu-academy"
								{@attach initCollapse}
							>
								<li>
									<a href="./scrollspy/#">
										<span class="icon-[tabler--books] size-5"></span>
										Courses
									</a>
								</li>
								<li>
									<a href="./scrollspy/#">
										<span class="icon-[tabler--list-details] size-5"></span>
										Course details
									</a>
								</li>
								<li class="space-y-0.5">
									<button
										class="collapse-toggle collapse-open:bg-base-content/10"
										id="sub-menu-academy-stats"
										data-collapse="#sub-menu-academy-stats-collapse"
										type="button"
										{@attach initCollapse}
									>
										<span class="icon-[tabler--chart-bar] size-5"></span>
										Stats
										<span
											class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
										></span>
									</button>
									<ul
										id="sub-menu-academy-stats-collapse"
										class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
										aria-labelledby="sub-menu-academy-stats"
									>
										<li>
											<a href="./scrollspy/#">
												<span class="icon-[tabler--chart-donut] size-5"></span>
												Intentions
											</a>
										</li>
									</ul>
								</li>
							</ul>
						</li>
					</ul>
				</li>
				<li>
					<a href="./scrollspy/#">
						<span class="icon-[tabler--mail] size-5"></span>
						<span class="overlay-minified:hidden">Further Page</span>
					</a>
				</li>

				<li>
					<a href="./scrollspy/#">
						<span class="icon-[tabler--shopping-bag] size-5"></span>
						<span class="overlay-minified:hidden">About</span>
					</a>
				</li>
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
		<div class=" bg-base-100 transition-all duration-300">
			<div id="scrollspy" class="space-y-4 pe-1">
				<div id="page-information">
					URL: <JsonData data={page.url} />
					<br />
					Pathname: <JsonData data={page.url.pathname} />
					<br />
					Hash: <JsonData data={page.url.hash} />
					<br />
					Search: <JsonData data={page.url.search} />
					<br />
					SearchParams: <JsonData data={page.url.searchParams} />
				</div>
				{@render children?.()}
			</div>
		</div>
	</div>
</div>
