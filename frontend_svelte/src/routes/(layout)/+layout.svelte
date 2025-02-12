<script lang="ts">
	import {
		Variant,
		Theming,
		extendingFlyonUIwithAdditionalMaterialDesignColors,
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

	const theming = $state(new Theming());

	let themeConfiguration: ColorConfig = $state({
		sourceColor: '#353c6e', // <= That's a good color!// '#769CDF',
		variant: Variant.TONAL_SPOT, // Variant.FIDELITY,//
		contrast: 0.0
	});
	// for theme picker:
	// let sourceColor = $state('#769CDF');
	// let variant = $state(Variant.TONAL_SPOT);
	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
	// let contrast = $state(0.0);

	let { children }: { children: Snippet } = $props();

	let mainContent: HTMLDivElement;
	let systemDark = $state(false);
	let mode: 'light' | 'dark' = $state('dark');

	const applyTheming: Action = (_node) => {
		systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		mode = systemDark ? 'dark' : 'light';

		// TBD: ensure that the material design tokens are not necessary any more.
		// Should be handled by TailwindCSS extension now in tailwind.config.js!
		// theming.ts creates the tokens and applies them to the DOM.
		extendingFlyonUIwithAdditionalMaterialDesignColors.forEach(
			(utilityClass, materialDesignToken) => {
				const tokenKebabCase = materialDesignToken
					.replace(/([a-z])([A-Z])/g, '$1-$2')
					.toLowerCase();
				Theming.addStyle(`.text-${utilityClass}`, [
					`color: var(--md-sys-color-${tokenKebabCase});`
				]);
				// TBD: check .ring
				Theming.addStyle(`.fill-${utilityClass}`, [`fill: var(--md-sys-color-${tokenKebabCase});`]);
				Theming.addStyle(`.caret-${utilityClass}`, [
					`caret-color: var(--md-sys-color-${tokenKebabCase});`
				]);
				Theming.addStyle(`.stroke-${utilityClass}`, [
					`stroke: var(--md-sys-color-${tokenKebabCase});`
				]);
				Theming.addStyle(`.border-${utilityClass}`, [
					`border-color: var(--md-sys-color-${tokenKebabCase});`
				]);
				Theming.addStyle(`.accent-${utilityClass}`, [
					`accent-color: var(--md-sys-color-${tokenKebabCase});`
				]);
				// TBD: check shadow!
				// TBD: check possibilities for applying opacity to those colors!
				Theming.addStyle(`.accent-${utilityClass}`, [
					`accent-color: var(--md-sys-color-${tokenKebabCase});`
				]);
				Theming.addStyle(`.decoration-${utilityClass}`, [
					`text-decoration-color: var(--md-sys-color-${tokenKebabCase});`
				]);

				// // TBD: causes trouble on all browsers on iPad
				// Theming.addStyle(`.placeholder:text-${utilityClass}`, [
				// 	`color: var(--md-sys-color-${tokenKebabCase});`
				// ]);
				// TBD: check .ring-offset
			}
		);

		let theme = $derived(theming.applyTheme(themeConfiguration, mode));

		$effect(() => {
			themeStore.set(theme);
		});
	};

	const toggleMode = () => {
		mode = mode === 'dark' ? 'light' : 'dark';
	};

	const { loggedIn } = page.data.session || false;

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

<div bind:this={mainContent} class="h-full" use:applyTheming>
	<nav
		class="navbar absolute start-0 top-0 z-[1] justify-between rounded-box bg-base-100 shadow md:flex md:items-stretch"
	>
		<div class="dropdown navbar-start inline-flex md:hidden rtl:[--placement:bottom-end]">
			<button
				type="button"
				class="dropdown-toggle btn btn-square btn-secondary btn-outline btn-sm"
				data-collapse="#default-navbar-dropdown"
				aria-controls="default-navbar-dropdown"
				aria-label="Toggle navigation"
			>
				<span class="icon-[tabler--menu-2] size-4 dropdown-open:hidden"></span>
				<span class="icon-[tabler--x] hidden size-4 dropdown-open:block"></span>
			</button>
			<ul
				class="dropdown-menu hidden bg-base-200 shadow-md shadow-outline text-base dropdown-open:opacity-100"
				aria-labelledby="default-navbar-dropdown"
			>
				<li class="dropdown-item">
					<a href="/" aria-label="Home"
						><span class="icon-[material-symbols--home-outline-rounded] size-6 bg-primary"
						></span></a
					>
				</li>
				<li class="dropdown-item"><a href="/docs" class="text-primary">Docs</a></li>
				<li class="dropdown-item"><a href="/playground" class="text-primary">Playground</a></li>
				<Guard>
					<hr class="-mx-2 my-3 border-outline" />
					<li class="dropdown-item"><a href="/dashboard" class="text-primary">Dashboard</a></li>
				</Guard>
			</ul>
		</div>
		<div class="navbar-start hidden items-center md:flex">
			<ul class="menu-horizontal flex items-center md:gap-4">
				<li>
					<a href="/" aria-label="Home"
						><span class="icon-[material-symbols--home-outline-rounded] size-6 bg-primary"
						></span></a
					>
				</li>
				<li><a href="/docs" class="text-primary">Docs</a></li>
				<li><a href="/playground" class="text-primary">Playground</a></li>
				<Guard>
					<hr class="-mx-2 my-3 border-outline" />
					<li><a href="/dashboard" class="text-primary">Dashboard</a></li>
				</Guard>
			</ul>
		</div>
		<div class="navbar-center flex flex-row">
			<div class="flex flex-col justify-center">
				<div class="text-title-small italic text-primary" style="line-height: 1;">Fullstack</div>
				<div
					class="text-title-small font-bold tracking-widest text-secondary"
					style="line-height: 1"
				>
					Sandbox
				</div>
			</div>
			<div class="text-heading-large navbar-center ml-1 flex items-center text-accent">23</div>
		</div>
		<div class="navbar-end flex items-center">
			<div class="dropdown flex items-center [--auto-close:inside] rtl:[--placement:bottom-end]">
				<span
					id="dropdown-menu-icon-user"
					class="dropdown-toggle {!loggedIn ? 'icon-[fa6-solid--user] size-6 bg-secondary' : ''}"
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
					class="dropdown-menu hidden bg-base-200 shadow-md shadow-outline dropdown-open:opacity-100"
					role="menu"
					aria-orientation="vertical"
					aria-labelledby="dropdown-menu-icon-user"
				>
					<li class="flex items-center gap-2">
						<span class="icon-[material-symbols--palette-outline] size-6"></span>
						<span class="grow"> Theming</span>
						<button aria-label="modeToggler">
							<label id="modeToggler" class="swap swap-rotate">
								<input type="checkbox" onclick={toggleMode} />
								<span class="icon-[tabler--sun] swap-on size-6"></span>
								<span class="icon-[tabler--moon] swap-off size-6"></span>
							</label>
						</button>
					</li>
					<li>
						<div class="w-48">
							<label class="label label-text flex" for="colorPicker">
								<span class="flex-grow">Source color:</span>
								<code>{themeConfiguration.sourceColor}</code>
							</label>
							<input
								class="w-full"
								type="color"
								id="colorPicker"
								name="color-picker"
								bind:value={themeConfiguration.sourceColor}
							/>
						</div>
					</li>
					<li>
						<div class="relative w-48">
							<label class="label label-text" for="themeVariant">Variant</label>
							<select
								class="select select-floating max-w-sm"
								aria-label="Select variant"
								id="themeVariant"
								bind:value={themeConfiguration.variant}
							>
								<option value={Variant.TONAL_SPOT}>Tonal Spot</option>
								<option value={Variant.MONOCHROME}>Monochrome</option>
								<option value={Variant.NEUTRAL}>Neutral</option>
								<option value={Variant.VIBRANT}>Vibrant</option>
								<option value={Variant.EXPRESSIVE}>Expressive</option>
								<option value={Variant.FIDELITY}>Fidelity</option>
								<option value={Variant.CONTENT}>Content</option>
								<option value={Variant.RAINBOW}>Rainbow</option>
								<option value={Variant.FRUIT_SALAD}>Fruit Salad</option>
							</select>
						</div>
					</li>
					<li>
						<div class="w-48">
							<label class="label label-text flex" for="contrast">
								<span class="flex-grow">Contrast: </span>
								<code>{themeConfiguration.contrast}</code>
							</label>

							<input
								type="range"
								min={contrastMin}
								max={contrastMax}
								step={contrastStep}
								class="range w-full"
								aria-label="contrast"
								id="contrast"
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
						<hr class="-mx-2 my-5 border-outline" />
					</li>
					<li class="flex items-center gap-2">
						<span class="icon-[tabler--settings] size-6"></span>
						<span class="grow"> Settings</span>
					</li>
				</ul>
			</div>
			<div class="flex items-center md:ml-2">
				{#if !loggedIn}
					<button
						class="btn btn-secondary ml-2 rounded-full shadow shadow-secondary"
						aria-label="Log In"
					>
						<a href="/login">Log in</a>
					</button>
				{:else}
					<button
						class="btn btn-secondary btn-outline ml-2 rounded-full shadow shadow-secondary"
						aria-label="Log Out"
					>
						<a href="/logout">Log out</a>
					</button>
				{/if}
			</div>
		</div>
	</nav>

	<div class="mx-5 pt-24">
		{@render children?.()}
	</div>

	<!-- <JsonData data={theme}></JsonData> -->
</div>
