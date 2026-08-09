<script lang="ts">
	import { type SubmitFunction } from '@sveltejs/kit';
	import { onMount } from 'svelte';

	import Guard from '$components/Guard.svelte';
	import { type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
	import { type ThemeRuntimeContext } from '$lib/theming';
	import { initDropdown } from '$lib/userInterface';

	import LoginOutButton from './LoginOutButton.svelte';
	import Logo from './Logo.svelte';
	import ArtificialIntelligencePicker from './playground/components/ArtificialIntelligencePicker.svelte';
	import ThemePicker from './playground/components/ThemePicker.svelte';
	import SidebarToggleButton from './SideBarToggleButton.svelte';

	let {
		loggedIn,
		updateProfileAccount,
		saveProfileAccount,
		artificialIntelligenceConfiguration,
		themeForm = $bindable(null),
		themeMode = $bindable(),
		themeConfiguration = $bindable(),
		parentUrl
	}: {
		loggedIn: boolean;
		updateProfileAccount: SubmitFunction;
		saveProfileAccount: () => Promise<void>;
		artificialIntelligenceConfiguration: ArtificialIntelligenceConfig;
		themeForm: HTMLFormElement | null;
		themeMode: ThemeRuntimeContext['mode'];
		themeConfiguration: ThemeRuntimeContext['themeConfiguration'];
		parentUrl: string | undefined;
	} = $props();

	let navBar: HTMLElement | null = $state(null);

	let avatarUrl: string | null = $state(null);

	async function loadAvatar() {
		try {
			const sessionId = localStorage.getItem('session_id');

			const response = await fetch('/apiproxies/msgraph?endpoint=/me/photo/$value', {
				method: 'GET',
				headers: sessionId ? { Authorization: `Bearer ${sessionId}` } : {}
			});

			if (!response.ok) {
				throw new Error(`Avatar request failed: ${response.status}`);
			}

			const blob = await response.blob();
			avatarUrl = URL.createObjectURL(blob);
		} catch (err) {
			console.error('Avatar load failed', err);
			avatarUrl = null;
		}
	}

	onMount(() => {
		loadAvatar();

		return () => {
			if (avatarUrl) URL.revokeObjectURL(avatarUrl);
		};
	});

	let artificialIntelligenceForm = $state<HTMLFormElement | null>(null);
</script>

{#snippet navbarPartItem(href: string, icon: string, text: string, textClasses?: string)}
	<li class="text-primary hidden items-center md:flex">
		<a {href} aria-label={text} class="flex items-center gap-1"
			><span class="{icon} size-5"></span>
			<span class={textClasses}>{text}</span>
		</a>
	</li>
{/snippet}

<nav
	class="navbar rounded-box shadow-shadow border-outline-variant bg-base-250 start-0 top-0 z-1 flex justify-between border-1 border-b px-3 shadow-md transition-all duration-300 max-sm:h-14 md:items-center"
	bind:this={navBar}
>
	<!-- {@attach updateNavbarBottom} -->
	<div class="navbar-start rtl:[--placement:bottom-end]">
		<ul class="menu menu-horizontal flex flex-nowrap items-center">
			<SidebarToggleButton
				extraClasses="hidden sm:flex"
				overlayModifier={{ 'data-overlay-minifier': '#collapsible-mini-sidebar' }}
			/>
			<SidebarToggleButton
				extraClasses="sm:hidden"
				overlayModifier={{ 'data-overlay': '#collapsible-mini-sidebar' }}
			/>
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
					'hidden xl:block'
				)}
			</Guard>
			<!-- {@render navbarPartItem(
						'/features',
						'icon-[mdi--feature-highlight]',
						'Features',
						'hidden xl:block'
					)}
					{@render navbarPartItem('/apps', 'icon-[tabler--apps]', 'Apps', 'hidden xl:block')}
					{@render navbarPartItem(
						'/construction',
						'icon-[maki--construction]',
						'Construction',
						'hidden xl:block'
					)} -->
		</ul>
	</div>
	<Logo />
	<div class="navbar-end">
		<button
			class="btn btn-sm btn-text btn-circle text-primary size-8.5 md:hidden"
			aria-label="Search"
		>
			<span class="icon-[tabler--search] size-5"></span>
		</button>
		<div class="input bg-base-150 mx-2 max-w-56 rounded-full max-md:hidden">
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
				class="dropdown-toggle {!loggedIn ? 'icon-[fa6-solid--user] bg-secondary size-5' : ''}"
				role="button"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="User Menu"
			>
				{#if loggedIn}
					<!-- {#if avatarUrl} -->
					<img
						src={avatarUrl ?? ''}
						alt="your profile"
						class="not-hover:mask-radial-t-0% h-10 min-w-10 rounded-full not-hover:mask-radial-from-40%"
					/>
					<!-- {:else}
							<span class="icon-[fa6-solid--user] bg-secondary size-5 h-10 w-10 rounded-full"
							></span>
						{/if} -->
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
					bind:mode={themeMode}
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
						<span class="icon-[tabler--eye] bg-secondary size-5"></span>
						<span class="text-secondary grow">Show welcome modal</span>
					</button>
				</li>
			</ul>
		</div>
		<div class="hidden items-center sm:flex md:ml-2">
			<LoginOutButton {loggedIn} {parentUrl} />
		</div>
	</div>
</nav>
