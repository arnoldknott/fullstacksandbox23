<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { initDropdown, initOverlay } from '$lib/userInterface';
	import { type Snippet } from 'svelte';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { Variant, type ColorConfig } from '$lib/theming';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
	import ThemePicker from '../../../components/ThemePicker.svelte';
	import ArtificialIntelligencePicker from '../../../components/ArtificialIntelligencePicker.svelte';
	import { afterNavigate } from '$app/navigation';
	import { onMount } from 'svelte';
	import type { SidebarItemContent } from '$lib/types';
	import SidebarItem from './SidebarItem.svelte';
	let { children }: { children: Snippet } = $props();

	let sidebarLinks: SidebarItemContent[] = $state([
		{
			name: 'Page 1',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page1'),
			icon: 'icon-[tabler--user]',
			id: 'page1',
			items: []
		},
		{
			name: 'Page 2',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page2'),
			icon: 'icon-[icon-park-outline--page]',
			id: 'page2',
			items: [
				{
					id: 'page2-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#loreum1'
				},
				{
					id: 'page2-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#sub-category',
					id: 'page2-sub-category',
					items: [
						{
							id: 'page2-loreum3',
							name: 'Loreum 3',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3'
						},
						{
							id: 'page2-loreum4',
							name: 'Loreum 4',
							icon: 'icon-[mdi--text]',
							hash: '#loreum4'
						}
					]
				},
				{
					id: 'page2-loreum5',
					name: 'Loreum 5',
					icon: 'icon-[mdi--text]',
					hash: '#loreum5'
				},
				{
					id: 'page2-loreum6',
					name: 'Loreum 6',
					icon: 'icon-[mdi--text]',
					hash: '#loreum6'
				}
			]
		},
		{
			name: 'Page 3',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page3'),
			icon: 'icon-[icon-park-outline--page]',
			id: 'page3',
			items: [
				{
					id: 'page3-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#loreum1'
				},
				{
					id: 'page3-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2'
				},
				{
					id: 'page3-loreum2a',
					name: 'Loreum 2a',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2a'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#sub-category-page3',
					id: 'page3-sub-category',
					items: [
						{
							id: 'page3-loreum3p1',
							name: 'Loreum 3.1',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3p1'
						},
						{
							id: 'page3-loreum3p2',
							name: 'Loreum 3.2',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3p2'
						}
					]
				},
				{
					id: 'page3-loreum4',
					name: 'Loreum 4',
					icon: 'icon-[mdi--text]',
					hash: '#loreum4'
				},
				{
					id: 'page3-loreum5',
					name: 'Loreum 5',
					icon: 'icon-[mdi--text]',
					hash: '#loreum5'
				}
			]
		},
		{
			id: 'further-page',
			name: 'Further Page',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page4'),
			icon: 'icon-[tabler--mail]',
			items: [
				{
					id: 'page4-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#loreum1'
				},
				{
					id: 'page4-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#sub-category-page4',
					id: 'page4-sub-category',
					items: [
						{
							id: 'page4-loreum3',
							name: 'Loreum 3',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3'
						},
						{
							id: 'page4-loreum4',
							name: 'Loreum 4',
							icon: 'icon-[mdi--text]',
							hash: '#loreum4'
						}
					]
				},
				{
					id: 'page4-sub-pages-section',
					name: 'Sub-pages',
					icon: 'icon-[mdi--text]',
					hash: '#page4-sub-pages-section'
				},
				{
					name: 'Sub-page 4.1',
					icon: 'icon-[mingcute--directory-line]',
					pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page4/page4-1'),
					id: 'page4p1',
					items: [
						{
							id: 'page4p1-loreum1',
							name: 'Loreum 1 pg4.1',
							icon: 'icon-[mdi--text]',
							pathname: resolve(
								'/(layout)/playground/user-interface/sidebar/recursion/page4/page4-1'
							),
							hash: '#loreum1'
						},
						{
							id: 'page4p1-loreum2',
							name: 'Loreum 2 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve(
								'/(layout)/playground/user-interface/sidebar/recursion/page4/page4-1'
							),
							hash: '#loreum2'
						}
					]
				},
				{
					name: 'Sub-page 4.2',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page4/page4-2'),
					id: 'page4p2',
					items: [
						{
							id: 'page4p2-loreum1',
							name: 'Loreum 1 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve(
								'/(layout)/playground/user-interface/sidebar/recursion/page4/page4-2'
							),
							hash: '#loreum1'
						},
						{
							id: 'page4p2-loreum2',
							name: 'Loreum 2 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve(
								'/(layout)/playground/user-interface/sidebar/recursion/page4/page4-2'
							),
							hash: '#loreum2'
						}
					]
				},
				{
					id: 'page4-loreum6',
					name: 'Loreum 6',
					icon: 'icon-[mdi--text]',
					hash: '#loreum6'
				}
			]
		},
		{
			name: 'Page 5',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page5'),
			icon: 'icon-[tabler--user]',
			id: 'page5',
			items: [
				{
					id: 'page5-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#loreum1'
				},
				{
					id: 'page5-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2'
				}
			]
		}
	]);
	let page6Content = $state([
		{
			name: 'Page 6',
			pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page6'),
			icon: 'icon-[solar--structure-linear]',
			id: 'page6',
			items: [
				{
					id: 'page6-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#loreum1'
				},
				{
					id: 'page6-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[fe--picture]',
					hash: '#loreum2'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#sub-category',
					id: 'page6-sub-category',
					items: [
						{
							id: 'page6-loreum3',
							name: 'Loreum 3',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3'
						},
						{
							id: 'page6-loreum4',
							name: 'Loreum 4',
							icon: 'icon-[fluent--document-24-regular]',
							hash: '#loreum4'
						}
					]
				},
				{
					id: 'page6-loreum5',
					name: 'Loreum 5',
					icon: 'icon-[fe--picture]',
					hash: '#loreum5'
				},
				{
					id: 'page6-loreum6',
					name: 'Loreum 6',
					icon: 'icon-[fe--picture]',
					hash: '#loreum6'
				}
			]
		}
	]);

	let scrollspyParent: HTMLDivElement | null = $state(null);

	// afterNavigate((navigator) => {
	// 	if (navigator.to?.url.hash !== '' && scrollspyParent) {
	// 		console.log('=== afterNavigate - scroll to top ===');
	// 		// scrollspyParent.scrollTop = 0;
	// 		// scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
	// 		scrollspyParent.scrollTo(scrollspyParent.scrollLeft, 0);
	// 	}
	// });
	afterNavigate(({ to }) => {
		// reset scrolltop to zero, if no dedicated hash destination:
		if (scrollspyParent && !to?.url.hash) {
			scrollspyParent.scrollTop = 0;
			scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
		}
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
			// const original = scrollspyParent.scrollTop;
			// 		// scrolls to the other end of the scroll area and back to force scrollspy to recalculate positions
			// 		const alt =
			// 			original < 2 ? scrollspyParent.scrollHeight : original - scrollspyParent.scrollHeight;
			// 		scrollspyParent.scrollTop = alt;
			// 		scrollspyParent.dispatchEvent(new Event('scroll', { bubbles: true }));
			// 		requestAnimationFrame(() => {
			// 			scrollspyParent!.scrollTop = original;
			// 			scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
			// 		});
		}
	});

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
			><span class="{icon} size-6"></span>
			<span class={textClasses}>{text}</span>
		</a>
	</li>
{/snippet}

{#snippet sidebarPartItem(href: string, icon: string, text: string, listItemClasses?: string)}
	<li class="text-primary {listItemClasses}">
		<a {href}>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">{text}</span>
		</a>
	</li>
{/snippet}

<nav
	class="navbar rounded-box bg-base-100 shadow-shadow border-outline-variant relative sticky start-0 top-0 z-1 justify-between border-b shadow-sm md:flex md:items-center"
>
	<div class="navbar-start rtl:[--placement:bottom-end]">
		<ul class="menu menu-horizontal flex flex-nowrap items-center">
			{@render sidebarToggleButton('hidden sm:flex', {
				'data-overlay-minifier': '#collapsible-mini-sidebar'
			})}
			{@render sidebarToggleButton('sm:hidden', {
				'data-overlay': '#collapsible-mini-sidebar'
			})}
			<!-- {@render navbarPartItem('/features', 'icon-[mdi--feature-highlight]', 'Features')}
			{@render navbarPartItem('/apps', 'icon-[tabler--apps]', 'Apps')}
			{@render navbarPartItem(
				'/construction',
				'icon-[maki--construction]',
				'Construction',
				'hidden lg:block'
			)} -->
			<!-- {@render navbarPartItem(
				'/playground/user-interface/sidebar/hierarchy',
				'icon-[streamline--hierarchy-2]',
				'Hierarchy'
			)} -->
			{@render navbarPartItem(
				'/playground/user-interface/sidebar/recursion',
				'icon-[stash--arrows-switch]',
				'Recursion'
			)}
			<button
				class="btn btn-primary btn-gradient max-sm:btn-circle max-sm:ml-2 md:rounded-full"
				onclick={() =>
					sidebarLinks.length === 5 ? sidebarLinks.push(...page6Content) : sidebarLinks.pop()}
			>
				{#if sidebarLinks.length === 5}
					<span class="icon-[tabler--plus] size-5"></span>
					<div class="hidden md:block">add page 6</div>
				{:else if sidebarLinks.length === 6}
					<span class="icon-[tabler--minus] size-5"></span>
					<div class="hidden md:block">remove page 6</div>
				{/if}
			</button>
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
		<div class="hidden items-center sm:flex md:ml-2">
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
				{@render sidebarPartItem('/', 'icon-[material-symbols--home-outline-rounded]', 'Home')}
				<!-- {@render sidebarPartItem('/features', 'icon-[mdi--feature-highlight]', 'Features', 'md:hidden')}
				{@render sidebarPartItem('/apps', 'icon-[tabler--apps]', 'Apps', 'md:hidden')}
				{@render sidebarPartItem(
					'/construction',
					'icon-[maki--construction]',
					'Construction',
					'md:hidden'
				)} -->
				<!-- {@render sidebarPartItem(
					'/playground/user-interface/sidebar/hierarchy',
					'icon-[streamline--hierarchy-2]',
					'Hierarchy',
					'md:hidden'
				)} -->
				{@render sidebarPartItem(
					'/playground/user-interface/sidebar/recursion',
					'icon-[stash--arrows-switch]',
					'Recursion',
					'md:hidden'
				)}
			</ul>
			<div class="divider"></div>
			<ul class="menu p-0">
				{#each sidebarLinks as mainItem (mainItem.id)}
					<SidebarItem
						content={{ ...mainItem, pathname: mainItem.pathname || page.url.pathname }}
						topLevel={true}
					/>
				{/each}
				<li>
					<div class="items-center sm:hidden md:ml-2">
						<button
							class="btn btn-primary btn-outline shadow-primary ml-2 rounded-full shadow-sm"
							aria-label="LogInOut"
						>
							<a href="#top">LogInOut</a>
						</button>
					</div>
				</li>
			</ul>
		</div>
	</aside>
	<!-- TBD: how many div's inside each other are necessary here? Consider cleaning up! -->
	<div
		id="scrollspy"
		class="sm:overlay-minified:ps-19 bg-base-100 space-y-4 ps-64 pe-1 transition-all duration-300 max-sm:ps-0"
	>
		{@render children?.()}
	</div>
</div>
