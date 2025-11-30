<script lang="ts">
	import type { LayoutData } from './$types';
	import { SessionStatus } from '$lib/session';
	import { Variant, Theming, type ColorConfig } from '$lib/theming';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';

	import type { Action } from 'svelte/action';
	import { onMount, type Snippet } from 'svelte';
	import { page } from '$app/state';
	import Guard from '$components/Guard.svelte';
	import { initDropdown } from '$lib/userInterface';
	import ThemePicker from './playground/components/ThemePicker.svelte';
	import ArtificialIntelligencePicker from './playground/components/ArtificialIntelligencePicker.svelte';
	import { themeStore } from '$lib/stores';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { enhance } from '$app/forms';
	import { resolve } from '$app/paths';
	import WelcomeModal from './WelcomeModal.svelte';

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

		return () => {};
	};
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

<div bind:this={mainContent} class="mx-5 mt-5 h-full" use:applyTheming>
	<!-- TBD: put navbar into component -->
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
							<!-- works via JavaScript: onclick={() => window.HSOverlay.open(welcomeModal)}  -->
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

	<!-- TBD: put welcome modal into component -->
	<WelcomeModal
		bind:session={data.session}
		bind:artificialIntelligenceConfiguration
		bind:themeConfiguration
		bind:mode
		{updateProfileAccount}
		{saveProfileAccount}
	/>
	<!-- <div
		id="welcome-modal"
		class="overlay modal overlay-open:opacity-100 overlay-open:duration-300 modal-middle hidden [--body-scroll:true] [--overlay-backdrop:static]"
		data-overlay-keyboard="false"
		role="dialog"
		tabindex="-1"
		bind:this={welcomeModal}
	>
		<div class="modal-dialog modal-dialog-md">
			<div class="modal-content bg-base-300 shadow-outline ring-outline-variant shadow-lg ring">
				<div class="modal-header">
					<span class="icon-[ph--smiley] size-6"></span>
					<h3 class="modal-title grow pl-2">Welcome</h3>
					<div class="align-center flex grow flex-row justify-center">
						{page.data.session?.microsoftProfile.displayName}
					</div>

					<button
						type="button"
						class="btn btn-text btn-circle btn-sm absolute end-3 top-3"
						aria-label="Close"
						data-overlay="#welcome-modal"
					>
						<span class="icon-[tabler--x] size-4"></span>
					</button>
				</div>
				<div class="modal-body flex flex-wrap justify-between">
					<div class="align-center flex grow flex-row justify-center">
						<div class="flex flex-col justify-center">
							<div class="title-small text-primary italic" style="line-height: 1;">Fullstack</div>
							<div
								class="title-small text-secondary font-bold tracking-wide"
								style="line-height: 1"
							>
								Platform
							</div>
						</div>
						<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
					</div>
					<img
						src="/starnberger-see-unset-20230807.jpg"
						class="w-full rounded-lg mask-y-from-75% mask-y-to-100% mask-x-from-95% mask-x-to-100% opacity-70"
						alt="Bavarian lake Starnberger See in sunset"
					/>
					<div class="m-1 h-full w-full content-center p-4 text-justify font-semibold">
						Adjust your settings for Artificial Intelligence and Theme configuration now or later by
						clicking at your user icon in the top right corner.
					</div>
					<div class="grid grid-cols-1 gap-2 max-sm:w-full sm:grid-cols-2">
						<ul
							class="shadow-outline bg-base-250 m-1 h-[257px] w-full rounded rounded-xl p-4 shadow-inner"
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
						</ul>
						<ul
							class="shadow-outline bg-base-250 m-1 h-[257px] w-full rounded rounded-xl p-4 shadow-inner"
							role="menu"
							aria-orientation="vertical"
							aria-labelledby="dropdown-menu-icon-user"
						>
							<ThemePicker
								{updateProfileAccount}
								{saveProfileAccount}
								bind:themeForm
								bind:mode
								bind:themeConfiguration
							/>
						</ul>
					</div>
				</div>
				<div class="modal-footer">
					<form
						method="POST"
						action="/?/putme"
						use:enhance={async (input) => {
							input.formData.append(
								'ai-enabled',
								artificialIntelligenceConfiguration.enabled.toString()
							);
							input.formData.append('model-picker', artificialIntelligenceConfiguration.model);
							input.formData.append(
								'ai-temperature',
								artificialIntelligenceConfiguration.temperature.toString()
							);
							input.formData.append('color-picker', themeConfiguration.sourceColor);
							input.formData.append('variant-picker', themeConfiguration.variant);
							input.formData.append('contrast', themeConfiguration.contrast.toString());
							updateProfileAccount(input);
						}}
					>
						<button
							type="submit"
							onclick={() => (userUnregistered = false)}
							data-overlay="#welcome-modal"
							aria-label="Save profile"
							class="btn btn-primary-container btn-gradient shadow-outline rounded-full shadow-sm"
						>
							<span class="icon-[tabler--send-2]"></span>Save profile
						</button>
					</form>
				</div>
			</div>
		</div>
	</div> -->

	<div class="mt-5">
		{@render children?.()}
	</div>

	<!-- <JsonData data={theme}></JsonData> -->
</div>
