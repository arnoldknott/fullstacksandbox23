<script lang="ts">
	import {
		argbFromHex,
		themeFromSourceColor,
		applyTheme
	} from '@material/material-color-utilities';
	import type { Action } from 'svelte/action';
	import NavButton from '$components/NavButton.svelte';
	import UserButton from '$components/UserButton.svelte';
	// import type { LayoutData } from '../$types';
	import type { Snippet } from 'svelte';
	import { page } from '$app/stores';
	import Guard from '$components/Guard.svelte';

	// let { data, children }: { data: LayoutData; children: Snippet } = $props();
	let { children }: { children: Snippet } = $props();

	let mainContent: HTMLDivElement;
	// Get the theme from a hex color
	const theme = themeFromSourceColor(argbFromHex('#415f91'), [
		// {
		// 	name: "custom-1",
		// 	value: argbFromHex("#ff0000"),
		// 	blend: true,
		// },
	]);

	// Print out the theme as JSON
	console.log(JSON.stringify(theme, null, 2));

	const applyMaterialDesignTheme: Action = (_node) => {
		// read system setting dark / light mode on client side only - not during serve side rendering.
		const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

		console.log('=== src -routes - (layout) - applyMaterialDesignTheme - systemDark ===');
		console.log(systemDark);
		// Apply the theme to the body by updating custom properties for material tokens
		// applyTheme(theme, {target: document.body, dark: systemDark});
		applyTheme(theme, { target: mainContent, dark: systemDark });
	};

	// const session = data?.sessionData;
	// const loggedIn = session?.loggedIn || false;
	const { loggedIn } = $page.data.session || false;
	// const { session } = $page.data;

	let mode = $state('light');

	const toggleMode = () => {
		mode = mode === 'dark' ? 'light' : 'dark';
		// applyTheme(theme, {target: document.body, dark: mode === "dark"});
		applyTheme(theme, { target: mainContent, dark: mode === 'dark' });
		console.log('mode toggled to ' + mode);
	};

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
</script>

<svelte:window use:applyMaterialDesignTheme />

<!-- The class switches material design 3, whereas data-theme switches FlyonUI -->
<div bind:this={mainContent} class={`h-full ${mode}`} data-theme={mode}>
	<nav class="mx-2 p-2">
		<div class="flex w-full flex-wrap items-center justify-between">
			<div class="flex-grow space-x-4">
				<NavButton url="/" link="Home" />
				<NavButton url="/docs" link="Docs" />
				<NavButton url="/playground" link="Playground" />
				<Guard>
					<NavButton url="/protected" link="Protected" />
					<NavButton url="/dashboard" link="Dashboard" />
				</Guard>
			</div>
			<div class="flex space-x-4">
				<!-- Move this to component user button -->
				<!-- Implement check for user picture size and show svg instead, if no user picture available -->

				<!-- {#if loggedIn} -->
				<Guard>
					<img class="h-12 w-12 rounded-full" src="/api/v1/user/me/picture" alt="you" />
					{$page.data.session.microsoftProfile.displayName}
					<!-- TBD: remove the following one: -->
					<!-- {#if userPictureURL}
					<img class="h-12 w-12 rounded-full" src={userPictureURL} alt="you" />
				{/if} -->
				</Guard>
				<button aria-label="modeToggler">
					<label id="modeToggler" class="swap swap-rotate">
						<input type="checkbox" onclick={toggleMode} />
						<span class="icon-[tabler--sun] swap-on size-6"></span>
						<span class="icon-[tabler--moon] swap-off size-6"></span>
					</label>
				</button>
				<!-- {/if} -->
				<!-- Change this to using $page.data -> user -->
				{#if !loggedIn}
					<!-- <Guard> -->
					<!-- <NavButton url="/register" link="Register" invert /> -->
					<!-- data-sveltekit-preload-data="false" -->
					<!-- TBD: remove it here and set in hooks.Server.ts -->
					<NavButton pre_load={false} url={`/login?targetURL=${$page.url.href}`} link="Login" />
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

	<!-- <JsonData data={$page}></JsonData> -->

	<div>
		{@render children?.()}
	</div>
</div>

<style>
	@import './dark.css';
	@import './dark-hc.css';
	@import './dark-mc.css';
	@import './light.css';
	@import './light-hc.css';
	@import './light-mc.css';

	/* body {
		--p: rgb(65, 95, 145);
	} */
</style>
