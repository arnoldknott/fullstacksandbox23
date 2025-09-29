<script lang="ts">
	import type { LayoutData } from './$types';
	import { SessionStatus } from '$lib/session';
	import {
		Variant,
		Theming,
		// extendingFlyonUIwithAdditionalMaterialDesignColors,
		type ColorConfig
	} from '$lib/theming';

	import type { Action } from 'svelte/action';
	// import NavButton from '$components/NavButton.svelte';
	// import UserButton from '$components/UserButton.svelte';
	import { type Snippet } from 'svelte';
	import { page } from '$app/state';
	import Guard from '$components/Guard.svelte';
	import ThemePicker from './playground/components/ThemePicker.svelte';
	import { themeStore } from '$lib/stores';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { resolve } from '$app/paths';
	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	let userUnregistered = $derived(
		!data.session?.loggedIn
			? false
			: data.session?.status === SessionStatus.REGISTERED
				? false
				: true
	);

	const theming = $state(new Theming());

	// let themeConfiguration: ColorConfig = $state({
	// 	sourceColor: '#941ff4', // <= That's a good color!// '#353c6e' // '#769CDF',
	// 	variant: Variant.TONAL_SPOT, // Variant.FIDELITY,//
	// 	contrast: 0.0
	// });
	// $effect(() => {
	// 	if (page.data.session) {
	// 		console.log('=== layout - page.data.session.currentUser ===');
	// 		console.log(page.data.session);
	// 		console.log('=== layout - page.form ===');
	// 		console.log(page.form);
	// 		themeConfiguration.sourceColor = page.data.session.currentUser.user_profile.theme_color;
	// 		themeConfiguration.variant = page.data.session.currentUser.user_profile.theme_variant;
	// 		themeConfiguration.contrast = page.data.session.currentUser.user_profile.contrast;
	// 	}
	// });

	// TBD: refactor this to decently use the reactivity of Svelte - potentially use $derived!
	let themeConfiguration: ColorConfig = $state({
		sourceColor: data?.session?.currentUser?.user_profile.theme_color || '#941ff4', // <= That's a good color!// '#353c6e' // '#769CDF',
		variant: data?.session?.currentUser?.user_profile.theme_variant || Variant.TONAL_SPOT, // Variant.FIDELITY,//
		contrast: data?.session?.currentUser?.user_profile.contrast || 0.0
	});
	$effect(() => {
		if (data.session?.currentUser?.user_profile) {
			// console.log('=== layout - data.session.currentUser.user_profile ===');
			// console.log(data.session.currentUser.user_profile);
			data.session.currentUser.user_profile.theme_color = themeConfiguration.sourceColor;
			data.session.currentUser.user_profile.theme_variant = themeConfiguration.variant;
			data.session.currentUser.user_profile.contrast = themeConfiguration.contrast;
		}
	});

	// let { children }: { children: Snippet } = $props();

	let mainContent: HTMLDivElement;
	let systemDark = $state(false);
	let mode: 'light' | 'dark' = $state('dark');

	const applyTheming: Action = (_node) => {
		systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		mode = systemDark ? 'dark' : 'light';

		// TBD: ensure that the material design tokens are not necessary any more.
		// Should be handled by TailwindCSS extension now in tailwind.config.js!
		// theming.ts creates the tokens and applies them to the DOM.
		// Refactor: Since FlyonUI2 and TailwindCSS4 not necessary any more:
		// extendingFlyonUIwithAdditionalMaterialDesignColors.forEach(
		// 	(utilityClass, materialDesignToken) => {
		// 		const tokenKebabCase = materialDesignToken
		// 			.replace(/([a-z])([A-Z])/g, '$1-$2')
		// 			.toLowerCase();
		// 		Theming.addStyle(`.text-${utilityClass}`, [
		// 			`color: var(--md-sys-color-${tokenKebabCase});`
		// 		]);
		// 		// TBD: check .ring
		// 		Theming.addStyle(`.fill-${utilityClass}`, [`fill: var(--md-sys-color-${tokenKebabCase});`]);
		// 		Theming.addStyle(`.caret-${utilityClass}`, [
		// 			`caret-color: var(--md-sys-color-${tokenKebabCase});`
		// 		]);
		// 		Theming.addStyle(`.stroke-${utilityClass}`, [
		// 			`stroke: var(--md-sys-color-${tokenKebabCase});`
		// 		]);
		// 		Theming.addStyle(`.border-${utilityClass}`, [
		// 			`border-color: var(--md-sys-color-${tokenKebabCase});`
		// 		]);
		// 		Theming.addStyle(`.accent-${utilityClass}`, [
		// 			`accent-color: var(--md-sys-color-${tokenKebabCase});`
		// 		]);
		// 		// TBD: check shadow!
		// 		// TBD: check possibilities for applying opacity to those colors!
		// 		Theming.addStyle(`.accent-${utilityClass}`, [
		// 			`accent-color: var(--md-sys-color-${tokenKebabCase});`
		// 		]);
		// 		Theming.addStyle(`.decoration-${utilityClass}`, [
		// 			`text-decoration-color: var(--md-sys-color-${tokenKebabCase});`
		// 		]);

		// 		// // TBD: causes trouble on all browsers on iPad
		// 		// Theming.addStyle(`.placeholder:text-${utilityClass}`, [
		// 		// 	`color: var(--md-sys-color-${tokenKebabCase});`
		// 		// ]);
		// 		// TBD: check .ring-offset
		// 	}
		// );

		let theme = $derived(theming.applyTheme(themeConfiguration, mode));

		// page.data.session.currentUser.user_profile.theme_color = themeConfiguration.sourceColor;
		// page.data.session.currentUser.user_profile.theme_variant = themeConfiguration.variant;
		// page.data.session.currentUser.user_profile.contrast = themeConfiguration.contrast;
		// console.log('=== layout - applyTheming - page.data.session.currentUser.user_profile ===');
		// console.log(page.data.session.currentUser.user_profile);

		$effect(() => {
			themeStore.set(theme);
		});
	};

	const { loggedIn } = page.data.session || false;

	// Write theming to database:
	let profileAccountForm = $state<HTMLFormElement | null>(null);

	const saveProfileAccount = async () => {
		if (page.data.session?.loggedIn) {
			profileAccountForm?.requestSubmit();
			console.log('=== layout - saveProfileAccount - themeConfiguration ===');
			console.log($state.snapshot(themeConfiguration));
		}
	};

	const updateProfileAccount: SubmitFunction = async () => {
		// console.log('=== layout - updateProfileAccount - formData ===');
		// console.log(formData);

		return () => {};
	};

	// const { session } = page.data;

	// let userPictureURL: URL | undefined = $state(undefined);
	// onMount(async () => {
	// 	// this call does not have any authentication - remove it!
	// 	const response = await fetch('/api/v1/user/me/picture', { method: 'GET' });
	// 	if (!response.ok && response.status !== 200) {
	// 		console.log('layout - userPictureURL - response not ok');
	// 		console.log(response);
	// 	} else {
	// 		const pictureBlob = await response.blob();
	// 		// console.log('layout - userPictureURL - pictureBlob');
	// 		// console.log(pictureBlob);
	// 		if (pictureBlob.size === 0) {
	// 			console.log('layout - userPictureURL - no User picture available');
	// 			console.log(pictureBlob);
	// 		} else {
	// 			userPictureURL = URL.createObjectURL(pictureBlob);
	// 			// console.log('layout - userPictureURL');
	// 			// console.log(userPictureURL);
	// 		}
	// 	}
	// });
	// export const currentTheme = () => theme;
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
	<nav
		class="navbar rounded-box bg-base-100 sticky start-0 top-0 z-1 justify-between shadow-sm md:flex md:items-stretch"
	>
		<div class="dropdown navbar-start inline-flex md:hidden rtl:[--placement:bottom-end]">
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
				<div class="title-small text-secondary font-bold tracking-widest" style="line-height: 1">
					Sandbox
				</div>
			</div>
			<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
		</div>
		<div class="navbar-end flex items-center">
			<div class="dropdown flex items-center [--auto-close:inside] rtl:[--placement:bottom-end]">
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
							class="not-hover:mask-radial-t-0% h-10 w-10 rounded-full not-hover:mask-radial-from-40%"
							src={resolve('/apiproxies/msgraph') + '?endpoint=/me/photo/$value'}
							alt="you"
						/>
					{/if}
				</span>
				<ul
					class="dropdown-menu bg-base-200 text-neutral shadow-outline dropdown-open:opacity-100 hidden shadow-md"
					role="menu"
					aria-orientation="vertical"
					aria-labelledby="dropdown-menu-icon-user"
				>
					<ThemePicker
						{updateProfileAccount}
						{saveProfileAccount}
						bind:profileAccountForm
						bind:mode
						bind:themeConfiguration
					/>
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

	<div
		id="welcome-modal"
		class="overlay modal overlay-open:opacity-100 {userUnregistered
			? 'open opened'
			: 'hidden'} overlay-open:duration-300 modal-middle"
		role="dialog"
		tabindex="-1"
	>
		<div class="modal-dialog">
			<div class="modal-content bg-base-300">
				<div class="modal-header">
					<h3 class="modal-title">Welcome</h3>
					<button
						type="button"
						class="btn btn-text btn-circle btn-sm absolute end-3 top-3"
						aria-label="Close"
						data-overlay="#welcome-modal"
					>
						<span class="icon-[tabler--x] size-4"></span>
					</button>
				</div>
				<div class="modal-body">This is some placeholder content to show a welcome message.</div>
				<div class="modal-footer">
					<button type="button" onclick={() => (userUnregistered = false)} class="btn btn-primary"
						>Save profile</button
					>
				</div>
			</div>
		</div>
	</div>

	{#if userUnregistered}
		<div class="text-display-small text-error text-center">User not registered!</div>
		<div class="mt-5">
			{@render children?.()}
		</div>
	{:else}
		<div class="mt-5">
			{@render children?.()}
		</div>
	{/if}

	<!-- <JsonData data={theme}></JsonData> -->
</div>
