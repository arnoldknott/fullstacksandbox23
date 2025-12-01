<script lang="ts">
	import type { LayoutData } from './$types';
	import { SessionStatus } from '$lib/session';
	import { Variant, Theming, type ColorConfig } from '$lib/theming';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';

	import type { Action } from 'svelte/action';
	import { onMount, type Snippet } from 'svelte';
	import { page } from '$app/state';
	import Guard from '$components/Guard.svelte';
	import { initDropdown, initOverlay } from '$lib/userInterface';
	import ThemePicker from './playground/components/ThemePicker.svelte';
	import ArtificialIntelligencePicker from './playground/components/ArtificialIntelligencePicker.svelte';
	import { themeStore } from '$lib/stores';
	import { type SubmitFunction } from '@sveltejs/kit';
	// import { enhance } from '$app/forms';
	import { resolve } from '$app/paths';
	import WelcomeModal from './WelcomeModal.svelte';
	import { afterNavigate } from '$app/navigation';
	import type { SidebarItemContent } from '$lib/types';
	import SidebarItem from './SidebarItem.svelte';
	import LoginOutButton from './LoginOutButton.svelte';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	let userUnregistered = $derived(
		!data.session?.loggedIn
			? false
			: data.session?.status === SessionStatus.REGISTERED
				? false
				: true
	);

	let welcomeModal: HTMLDivElement | null = $state(null);

	onMount(() => {
		if (userUnregistered) {
			window.HSOverlay.open(welcomeModal);
		}
	});

	let artificialIntelligenceConfiguration: ArtificialIntelligenceConfig = $state({
		enabled: true,
		model: Model.MODEL1,
		temperature: 0.7
		// max_tokens: 2048
	});

	let artificialIntelligenceForm = $state<HTMLFormElement | null>(null);

	const theming = $state(new Theming());

	// TBD: refactor this to decently use the reactivity of Svelte - potentially use $derived!
	let themeConfiguration: ColorConfig = $state({
		sourceColor: data?.session?.currentUser?.user_profile.theme_color || '#941ff4', // <= That's a good color!// '#353c6e' // '#769CDF',
		variant: data?.session?.currentUser?.user_profile.theme_variant || Variant.TONAL_SPOT, // Variant.FIDELITY,//
		contrast: data?.session?.currentUser?.user_profile.contrast || 0.0
	});

	$effect(() => {
		if (data.session?.currentUser?.user_profile) {
			data.session.currentUser.user_profile.theme_color = themeConfiguration.sourceColor;
			data.session.currentUser.user_profile.theme_variant = themeConfiguration.variant;
			data.session.currentUser.user_profile.contrast = themeConfiguration.contrast;
		}
	});

	let mainContent: HTMLDivElement;
	let systemDark = $state(false);
	let mode: 'light' | 'dark' = $state('dark');

	const applyTheming: Action = (_node) => {
		systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		mode = systemDark ? 'dark' : 'light';

		let theme = $derived(theming.applyTheme(themeConfiguration, mode));

		$effect(() => {
			themeStore.set(theme);
		});
	};

	const { loggedIn } = page.data.session || false;

	// Write theming to database:
	let themeForm = $state<HTMLFormElement | null>(null);

	const saveProfileAccount = async () => {
		if (page.data.session?.loggedIn) {
			themeForm?.requestSubmit();
			// console.log('=== layout - saveProfileAccount - themeConfiguration ===');
			// console.log($state.snapshot(themeConfiguration));
		}
	};

	const updateProfileAccount: SubmitFunction = async () => {
		// console.log('=== layout - updateProfileAccount - formData ===');
		// console.log(formData);

		// Prevents page from updating/reloading:
		return () => {};
	};

	// Sidebar:
	let sidebarLinks: SidebarItemContent[] = $state([
		{
			name: 'Components',
			pathname: resolve('/(layout)/playground/components'),
			icon: 'icon-[tabler--components]',
			id: 'components',
			items: []
		},
		{
			name: 'Design',
			pathname: resolve('/(layout)/playground/design'),
			icon: 'icon-[fluent--design-ideas-20-regular]',
			id: 'design',
			items: [
				{
					name: 'Backgrounds',
					icon: 'icon-[mdi--palette-outline]',
					hash: '#backgrounds-and-surfaces',
					id: 'backgrounds'
				},
				{
					name: 'Foregrounds',
					icon: 'icon-[mdi--palette-outline]',
					hash: '#foregrounds',
					id: 'foregrounds'
				},
				{
					name: 'Components',
					icon: 'icon-[mdi--palette-outline]',
					hash: '#components',
					id: 'components'
				},
				{
					name: 'Playground',
					icon: 'icon-[mdi--playground-seesaw]',
					hash: '#playground',
					id: 'playground'
				},
				{
					name: 'FlyonUI',
					icon: 'icon-[mingcute--arrows-up-fill]',
					pathname: resolve('/(layout)/playground/design/flyonui'),
					id: 'flyonui'
				},
				{
					name: 'Material Design',
					icon: 'icon-[mdi--material-design]',
					pathname: resolve('/(layout)/playground/design/materialdesign'),
					id: 'material-design'
				},
				{
					name: 'Svelte',
					icon: 'icon-[tabler--brand-svelte]',
					pathname: resolve('/(layout)/playground/design/svelte'),
					id: 'svelte'
				}
			]
		}
	]);

	let scrollspyParent: HTMLDivElement | null = $state(null);

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
</script>

<!-- style="--p: 0.45 .2 125" -->
<!-- TBD: this one applies the Material Design variables on the body! -->
<!-- <svelte:window use:applyMaterialDesignTheme use:overrideFlyonUIColors /> -->
<!-- <svelte:window use:applyMaterialDesignTheme /> -->

<!-- The class switches material design 3, whereas data-theme switches FlyonUI -->
<!-- <div bind:this={mainContent} class={`h-full ${mode}`} data-theme={mode} style="--p: {primaryManual};"> -->
<!-- <div bind:this={mainContent} class={`h-full ${mode}`} data-theme={mode} style="--p: {primaryFromMaterialDesign};" use:applyTheming> -->
<!-- <div bind:this={mainContent} class={`h-full ${mode}`} data-theme={mode} use:applyTheming> -->
<!-- <div bind:this={mainContent} class="h-full {mode}" data-theme={mode} use:applyTheming> -->

<!-- <JsonData data={theme.configuration}></JsonData> -->

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

<div bind:this={mainContent} class="mx-5 mt-5 h-full" use:applyTheming>
	<!-- TBD: put navbar into component -->
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
				{@render navbarPartItem('/docs', 'icon-[oui--documentation]', 'Docs')}
				{@render navbarPartItem(
					'/playground',
					'icon-[mdi--playground-seesaw]',
					'Playground',
					'hidden lg:block'
				)}
				<Guard>
					{@render navbarPartItem(
						'/dashboard',
						'icon-[material-symbols--dashboard-outline-rounded]',
						'Dashboard',
						'hidden lg:block'
					)}
				</Guard>
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
				<span class="icon-[tabler--search] text-base-content/80 my-auto me-3 size-5 shrink-0"
				></span>
				<label class="sr-only" for="searchInput">Search</label>
				<input type="search" class="grow" placeholder="Search" id="searchInput" />
			</div>
			<div
				class="dropdown flex items-center [--auto-close:inside] rtl:[--placement:bottom-end]"
				{@attach initDropdown}
			>
				<span
					id="dropdown-menu-icon-user"
					class="dropdown-toggle {!loggedIn ? 'icon-[fa6-solid--user] bg-secondary size-6' : ''}"
					role="button"
					aria-haspopup="menu"
					aria-expanded="false"
					aria-label="User Menu"
				>
					{#if loggedIn}
						<img
							class="not-hover:mask-radial-t-0% h-10 min-w-10 rounded-full not-hover:mask-radial-from-40%"
							src={resolve('/apiproxies/msgraph') + '?endpoint=/me/photo/$value'}
							alt="you"
						/>
					{/if}
				</span>
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
						<button
							aria-label="show Modal"
							type="button"
							class="dropdown-item dropdown-close"
							aria-haspopup="dialog"
							aria-expanded="false"
							aria-controls="welcome-modal"
							data-overlay="#welcome-modal"
						>
							<span class="icon-[tabler--eye] bg-secondary size-6"></span>
							<span class="text-secondary grow">Show welcome modal</span>
						</button>
					</li>
				</ul>
			</div>
			<div class="hidden items-center sm:flex md:ml-2">
				<LoginOutButton {loggedIn} />
				<!-- {#if !loggedIn}
					<button
						class="btn btn-neutral shadow-neutral ml-2 rounded-full shadow-sm"
						aria-label="Log In"
					>
						<a href="/login">Log in</a>
					</button>
				{:else}
					<button
						class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
						aria-label="Log Out"
					>
						<a href="/logout">Log out</a>
					</button>
				{/if} -->
			</div>
		</div>
	</nav>
	<!--
	<nav
		class="navbar rounded-box bg-base-100 border-outline-variant sticky start-0 top-0 z-1 justify-between border-b shadow-sm md:flex md:items-stretch"
	>
		<div
			class="dropdown navbar-start inline-flex md:hidden rtl:[--placement:bottom-end]"
			{@attach initDropdown}
		>
			<button
				type="button"
				class="dropdown-toggle btn btn-square btn-neutral btn-outline btn-sm"
				data-collapse="#default-navbar-dropdown"
				aria-controls="default-navbar-dropdown"
				aria-label="Toggle navigation"
			>
				<span class="icon-[tabler--menu-2] bg-neutral dropdown-open:hidden size-4"></span>
				<span class="icon-[tabler--x] bg-neutral dropdown-open:block hidden size-4"></span>
			</button>
			<ul
				class="dropdown-menu bg-base-200 shadow-outline dropdown-open:opacity-100 hidden text-base shadow-md"
				aria-labelledby="default-navbar-dropdown"
			>
				<li class="dropdown-item">
					<a href="/" aria-label="Home"
						><span class="icon-[material-symbols--home-outline-rounded] bg-neutral size-6"
						></span></a
					>
				</li>
				<li class="dropdown-item"><a href="/docs" class="text-neutral">Docs</a></li>
				<li class="dropdown-item"><a href="/playground" class="text-neutral">Playground</a></li>
				<Guard>
					<hr class="border-outline -mx-2 my-3" />
					<li class="dropdown-item"><a href="/dashboard" class="text-neutral">Dashboard</a></li>
				</Guard>
			</ul>
		</div>
		<div class="navbar-start hidden items-center md:flex">
			<ul class="menu-horizontal flex items-center md:gap-4">
				<li>
					<a href="/" aria-label="Home"
						><span class="icon-[material-symbols--home-outline-rounded] bg-neutral size-6"
						></span></a
					>
				</li>
				<li><a href="/docs" class="text-neutral">Docs</a></li>
				<li><a href="/playground" class="text-neutral">Playground</a></li>
				<Guard>
					<hr class="border-outline -mx-2 my-3" />
					<li><a href="/dashboard" class="text-neutral">Dashboard</a></li>
				</Guard>
			</ul>
		</div>
		<div class="navbar-center flex flex-row">
			<div class="flex flex-col justify-center">
				<div class="title-small text-primary italic" style="line-height: 1;">Fullstack</div>
				<div class="title-small text-secondary font-bold tracking-wide" style="line-height: 1">
					Platform
				</div>
			</div>
			<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
		</div>
		<div class="navbar-end flex items-center">
			<div
				class="dropdown flex items-center [--auto-close:inside] rtl:[--placement:bottom-end]"
				{@attach initDropdown}
			>
				<span
					id="dropdown-menu-icon-user"
					class="dropdown-toggle {!loggedIn ? 'icon-[fa6-solid--user] bg-secondary size-6' : ''}"
					role="button"
					aria-haspopup="menu"
					aria-expanded="false"
					aria-label="User Menu"
				>
					{#if loggedIn}
						<img
							class="not-hover:mask-radial-t-0% h-10 min-w-10 rounded-full not-hover:mask-radial-from-40%"
							src={resolve('/apiproxies/msgraph') + '?endpoint=/me/photo/$value'}
							alt="you"
						/>
					{/if}
				</span>
				<ul
					class="dropdown-menu bg-base-200 shadow-outline dropdown-open:opacity-100 hidden shadow-md"
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
						<button
							aria-label="show Modal"
							type="button"
							class="dropdown-item dropdown-close"
							aria-haspopup="dialog"
							aria-expanded="false"
							aria-controls="welcome-modal"
							data-overlay="#welcome-modal"
						>
							<span class="icon-[tabler--eye] bg-secondary size-6"></span>
							<span class="text-secondary grow">Show welcome modal</span>
						</button>
					</li>
				</ul>
			</div>
			<div class="flex items-center md:ml-2">
				{#if !loggedIn}
					<button
						class="btn btn-neutral shadow-neutral ml-2 rounded-full shadow-sm"
						aria-label="Log In"
					>
						<a href="/login">Log in</a>
					</button>
				{:else}
					<button
						class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
						aria-label="Log Out"
					>
						<a href="/logout">Log out</a>
					</button>
				{/if}
			</div>
		</div>
	</nav>
	-->

	<WelcomeModal
		bind:session={data.session}
		bind:artificialIntelligenceConfiguration
		bind:themeConfiguration
		bind:mode
		{updateProfileAccount}
		{saveProfileAccount}
	/>

	<div
		id="scrollspy-scrollable-parent"
		class="grid h-screen overflow-y-auto"
		bind:this={scrollspyParent}
	>
		<aside
			id="collapsible-mini-sidebar"
			class="overlay overlay-minified:w-19 overlay-open:translate-x-0 drawer drawer-start border-base-content/20 hidden w-66 border-e pt-26 [--auto-close:sm] sm:absolute sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
			tabindex="-1"
			{@attach initOverlay}
		>
			<div class="drawer-body px-2 pt-4">
				<ul class="menu p-0">
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
							<LoginOutButton {loggedIn} />
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

	<!-- <div class="mt-5">
		{@render children?.()}
	</div> -->

	<!-- <JsonData data={theme}></JsonData> -->
</div>
