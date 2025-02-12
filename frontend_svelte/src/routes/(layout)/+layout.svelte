<script lang="ts">
	import {
		Variant,
		Theming,
		extendingFlyonUIwithAdditionalMaterialDesignColors,
		type ColorConfig
	} from '$lib/theming';

	import type { Action } from 'svelte/action';
	import NavButton from '$components/NavButton.svelte';
	import UserButton from '$components/UserButton.svelte';
	import { type Snippet } from 'svelte';
	import { page } from '$app/state';
	import Guard from '$components/Guard.svelte';
	import ThemePicker from '$components/ThemePicker.svelte';
	import { themeStore } from '$lib/stores';

	const theming = $state(new Theming());

	let themeConfiguration: ColorConfig = $state({
		sourceColor: '#353c6e', // <= That's a good color!// '#769CDF',
		variant: Variant.TONAL_SPOT, // Variant.FIDELITY,//
		contrast: 0.0
	});

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
	<nav class="mx-2 p-2">
		<div class="flex w-full flex-wrap items-center justify-between">
			<div class="flex-grow space-x-4">
				<NavButton url="/" link="Home" />
				<NavButton url="/docs" link="Docs" />
				<NavButton url="/playground" link="Playground" />
				<Guard>
					<NavButton url="/dashboard" link="Dashboard" />
				</Guard>
			</div>
			<div class="flex space-x-4">
				<!-- Move this to component user button -->
				<!-- Implement check for user picture size and show svg instead, if no user picture available -->

				<!-- {#if loggedIn} -->
				<Guard>
					<img class="h-12 w-12 rounded-full" src="/api/v1/user/me/picture" alt="you" />
					{page.data.session.microsoftProfile.displayName}
					<!-- TBD: remove the following one: -->
					<!-- {#if userPictureURL}
					<img class="h-12 w-12 rounded-full" src={userPictureURL} alt="you" />
				{/if} -->
				</Guard>
				<!-- {themeConfiguration.contrast} -->
				<ThemePicker bind:values={themeConfiguration} />
				<!-- {tenFold} -->
				<button aria-label="modeToggler">
					<label id="modeToggler" class="swap swap-rotate">
						<input type="checkbox" onclick={toggleMode} />
						<span class="icon-[tabler--sun] swap-on size-6"></span>
						<span class="icon-[tabler--moon] swap-off size-6"></span>
					</label>
				</button>
				<!-- {/if} -->
				<!-- Change this to using page.data -> user -->
				{#if !loggedIn}
					<!-- <Guard> -->
					<!-- <NavButton url="/register" link="Register" invert /> -->
					<!-- data-sveltekit-preload-data="false" -->
					<!-- TBD: remove it here and set in hooks.Server.ts -->
					<NavButton pre_load={false} url={`/login?targetURL=${page.url.href}`} link="Login" />
				{:else}
					<UserButton />
					<!-- needs to redirect to /home and delete session information -->
					<!-- TBD: write tests for logout -->
					<!-- data-sveltekit-preload-data="false" -->
					<NavButton pre_load={false} url="/logout" link="Logout" />
				{/if}
			</div>
		</div>
	</nav>

	<div class="mx-5">
		{@render children?.()}
	</div>

	<!-- <JsonData data={theme}></JsonData> -->
</div>
