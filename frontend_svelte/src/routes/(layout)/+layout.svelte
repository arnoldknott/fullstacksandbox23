<script lang="ts">
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
	// import ThemePicker from '$components/ThemePicker.svelte';
	import { themeStore } from '$lib/stores';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { enhance } from '$app/forms';
	import type { LayoutData } from './$types';
	let { data, children }: { data: LayoutData; children: Snippet } = $props();

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

	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;

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

	const toggleMode = () => {
		mode = mode === 'dark' ? 'light' : 'dark';
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
		class="navbar rounded-box bg-base-100 z-1 sticky start-0 top-0 justify-between shadow-sm md:flex md:items-stretch"
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
			<!-- Debugging select - auto closes the dropdown - START-->
			<!-- <div class="dropdown relative inline-flex">
				<button
					id="dropdown-default"
					type="button"
					class="dropdown-toggle btn btn-primary"
					aria-haspopup="menu"
					aria-expanded="false"
					aria-label="Dropdown"
				>
					Dropdown
					<span class="icon-[tabler--chevron-down] dropdown-open:rotate-180 size-4"></span>
				</button>
				<ul
					class="dropdown-menu dropdown-open:opacity-100 hidden min-w-60"
					role="menu"
					aria-orientation="vertical"
					aria-labelledby="dropdown-default"
				>
					<li>Dropdown item 1</li>
					<li>Dropdown item 2</li>
					<li>
						<select class="select max-w-sm appearance-none" aria-label="select">
							<option disabled selected>Pick your favorite Movie</option>
							<option>The Godfather</option>
							<option>The Shawshank Redemption</option>
							<option>Pulp Fiction</option>
							<option>The Dark Knight</option>
							<option>Schindler's List</option>
						</select>
					</li>
				</ul>
			</div> -->
			<!-- Debugging select - auto closes the dropdown - END -->
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
						<img class="h-10 w-10 rounded-full" src="/api/v1/user/me/picture" alt="you" />
					{/if}
				</span>
				<ul
					class="dropdown-menu bg-base-200 text-neutral shadow-outline dropdown-open:opacity-100 hidden shadow-md"
					role="menu"
					aria-orientation="vertical"
					aria-labelledby="dropdown-menu-icon-user"
				>
					<form
						method="POST"
						action="/?/putme"
						id="user_profile_and_account"
						use:enhance={updateProfileAccount}
						bind:this={profileAccountForm}
					>
						<li class="flex items-center gap-2">
							<span class="icon-[material-symbols--palette-outline] size-6"></span>
							<span class="grow"> Theming</span>
							<button aria-label="modeToggler" type="button">
								<label for="mode-toggler" class="swap swap-rotate">
									<input id="mode-toggler" type="checkbox" onclick={toggleMode} />
									<span class="icon-[tabler--moon] swap-on size-6"></span>
									<span class="icon-[tabler--sun] swap-off size-6"></span>
								</label>
							</button>
						</li>
						<li>
							<div class="w-48">
								<label class="label label-text flex" for="color-picker">
									<span class="grow">Source color:</span>
									<code>{themeConfiguration.sourceColor}</code>
								</label>
								<input
									class="w-full"
									type="color"
									id="color-picker"
									name="color-picker"
									onchange={() => saveProfileAccount()}
									bind:value={themeConfiguration.sourceColor}
								/>
							</div>
						</li>
						<li>
							<div class="relative w-48">
								<label class="label label-text" for="theme-variant">Variant</label>
								<select
									class="select select-floating max-w-sm"
									aria-label="Select variant"
									id="theme-variant"
									name="variant-picker"
									onchange={() => saveProfileAccount()}
									bind:value={themeConfiguration.variant}
								>
									<option value={Variant.TONAL_SPOT}>Tonal Spot</option>
									<!-- <option value={Variant.MONOCHROME}>Monochrome</option> -->
									<option value={Variant.NEUTRAL}>Neutral</option>
									<option value={Variant.VIBRANT}>Vibrant</option>
									<!-- <option value={Variant.EXPRESSIVE}>Expressive</option> -->
									<option value={Variant.FIDELITY}>Fidelity</option>
									<option value={Variant.CONTENT}>Content</option>
									<option value={Variant.RAINBOW}>Rainbow</option>
									<!-- <option value={Variant.FRUIT_SALAD}>Fruit Salad</option> -->
								</select>
							</div>
						</li>
						<li>
							<div class="w-48">
								<label class="label label-text flex" for="contrast">
									<span class="grow">Contrast: </span>
									<code>{themeConfiguration.contrast}</code>
								</label>

								<input
									type="range"
									min={contrastMin}
									max={contrastMax}
									step={contrastStep}
									class="range w-full"
									aria-label="contrast"
									name="contrast"
									id="contrast"
									onchange={() => saveProfileAccount()}
									bind:value={themeConfiguration.contrast}
								/>
								<!-- <div class="flex w-full justify-between px-2 text-xs">
										{#each allContrasts as _}
											<span>|</span>
										{/each}
									</div> -->
							</div>
						</li>
						<li>
							<hr class="border-outline -mx-2 my-5" />
						</li>
						<li class="flex items-center gap-2">
							<span class="icon-[tabler--settings] size-6"></span>
							<span class="grow"> Settings</span>
						</li>
					</form>
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

	<div class="mt-5">
		{@render children?.()}
	</div>

	<!-- <JsonData data={theme}></JsonData> -->
</div>
