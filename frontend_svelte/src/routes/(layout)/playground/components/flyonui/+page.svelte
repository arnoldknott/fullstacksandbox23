<script lang="ts">
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	// import { createRawSnippet, type Snippet } from 'svelte';
	import type { IOverlay } from 'flyonui/flyonui';
	import ColorTileFlyonUi from '$components/ColorTileFlyonUI.svelte';
	import { type AppTheme } from '$lib/theming';
	import { themeStore } from '$lib/stores';
	// import { hexFromArgb } from '@material/material-color-utilities';
	import { onDestroy } from 'svelte';
	import JsonData from '$components/JsonData.svelte';
	// import {Theming }from '$lib/theming';

	// const createdComponent: Snippet = createRawSnippet(() => {
	// return {
	// 	render: () => ``
	// 	// setup: (element: Element) => {}
	// };
	// });

	// let isDrawerOpen = $state(false);

	// const toggleDrawer = () => {
	// 	isDrawerOpen = !isDrawerOpen;
	// 	console.log('Drawer toggled to ' + isDrawerOpen);
	// }
	// const closeDrawer = () => isDrawerOpen = false;

	let showSections = $state({
		colors: true,
		utilityClasses: true
	});

	let sourceColor = $state('#769CDF');
	let variant = $state('TONAL_SPOT');
	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
	const allContrasts = Array.from(
		{ length: (contrastMax - contrastMin) / contrastStep + 1 },
		(_, i) => contrastMin + i * contrastStep
	);
	let contrast = $state(0.0);
	// $effect(() => console.log('sourceColor:', sourceColor, 'variant:', variant, 'contrast:', contrast));

	const loadHSOverlay = async () => {
		const { HSOverlay } = await import('flyonui/flyonui.js');
		return HSOverlay;
	};

	let myModal: HTMLElement;
	let overlay: IOverlay | undefined = $state();

	$effect(() => {
		loadHSOverlay().then((loadHSOverlay) => {
			overlay = new loadHSOverlay(myModal);
		});
	});

	const openModal = () => {
		overlay?.open();
	};

	// This is getting the resolved CSS after FlyonUI, Tailwind CSS and so on processing - don't alter that."
	// $effect(() => Theming.addBackgroundUtilityClass('primary-container', ['var(--md-sys-color-primary-container)']));
	// $effect(() => Theming.addBackgroundUtilityClass('inverse-primary', ['var(--md-sys-color-inverse-primary)']));
	// $effect(() => Theming.addFillUtilityClass('inverse-primary', ['var(--md-sys-color-inverse-primary)']));
	// $effect(() => {
	// 	Theming.addStyle('.bg-primary-container', ['background-color: var(--md-sys-color-primary-container)'])
	// 	Theming.addStyle('.bg-inverse-primary', ['background-color: var(--md-sys-color-inverse-primary)'])
	// 	Theming.addStyle('.fill-inverse-primary', ['fill: var(--md-sys-color-inverse-primary)'])
	// 	});// wouldn't it be the same as just using the scoped style further down?

	let theme = $state({} as AppTheme);
	const unsubscribeThemeStore = themeStore.subscribe((value) => {
		// console.log('themeStore:', value);
		theme = value;
	});

	// let inversePrimaryHex = $derived.by(() => {
	// 	if (!theme.currentMode) {
	// 		return '';
	// 	} else {
	// 		let colors = theme[theme.currentMode].colors;
	// 		return hexFromArgb(colors['inversePrimary']);
	// 	}
	// });
	// let surfaceTintHex = $derived.by(() => {
	// 	if (!theme.currentMode) {
	// 		console.log('=== no-theme ===');
	// 		return '';
	// 	} else {
	// 		let colors = theme[theme.currentMode].colors;
	// 		const color = hexFromArgb(colors['surfaceTint']);
	// 		return color;
	// 	}
	// });

	onDestroy(() => {
		unsubscribeThemeStore();
	});

	// const additionalColors = $derived([
	// 	{
	// 		name: 'inverse-primary',
	// 		value: inversePrimaryHex
	// 	},
	// 	{
	// 		name: 'surface-tint',
	// 		value: surfaceTintHex
	// 	}
	// ]);

	// $effect(() => {
	// 	// TBD: consider applying variables instead of values?
	// 	// and only once - then the content of the variables get updated
	// 	// from applyTheme in (layout)/layout.svelte, but not the utility classes
	// 	additionalColors.forEach((color) => {
	// 		// // utlitity classes:
	// 		// // TBD: check .ring
	// 		// Theming.addStyle(`.fill-${color.name}`, [
	// 		// `fill: ${color.value};`
	// 		// ]);
	// 		// Theming.addStyle(`.caret-${color.name}`, [
	// 		// 	`caret-color: ${color.value};`
	// 		// ]);
	// 		// Theming.addStyle(`.stroke-${color.name}`, [
	// 		// 	`stroke: ${color.value};`
	// 		// ]);
	// 		// Theming.addStyle(`.border-${color.name}`, [
	// 		// 	`border-color: ${color.value};`
	// 		// ]);
	// 		// Theming.addStyle(`.accent-${color.name}`, [
	// 		// 	`accent-color: ${color.value};`
	// 		// ]);
	// 		// // TBD: check shadow!
	// 		// // TBD: check possibilities for applying opacity to those colors!
	// 		// Theming.addStyle(`.accent-${color.name}`, [
	// 		// 	`accent-color: ${color.value};`
	// 		// ]);
	// 		// Theming.addStyle(`.decoration-${color.name}`, [
	// 		// 	`text-decoration-color: ${color.value};`
	// 		// ]);
	// 		// // TBD: causes trouble on all browsers on iPad
	// 		// // Theming.addStyle(`.placeholder:text-${color.name}`, [
	// 		// // 	`color: ${color.value};`
	// 		// // ]);
	// 		// // TBD: check .ring-offset
	// 		// // component classes:
	// 		// Theming.addStyle(`.btn-${color.name}`, [
	// 		// 	`--btn-color: ${color.value};`
	// 		// ]);
	// 	});
	// });

	// // When applying to another variable, the flyonUI variables work, like --p, --pc, ... - they are oklch values!
	// // When assigning static, the material design tokens work, like primary, primary-content, ... - they are hex values!
	// // is this true?
	// $effect(()=> {
	// 	console.log("=== Theming for utility classes is triggered ===")
	// 	Theming.addStyle(".badge-inverse-primary", ["background-color: var(--md-sys-color-inverse-primary);", "color: var(--md-sys-color-on-primary);"])
	// 	Theming.addStyle(".btn-inverse-primary", ["--btn-color: var(--ip);"])
	// 	// Theming.addStyle(".btn-inverse-primary", ["--btn-color: var(--md-sys-color-inverse-primary);"])
	// 	Theming.addStyle(".accent-inverse-primary", ["accent-color: var(--ip);"])// note: this is a color utility, not a component utility!
	// 	Theming.addStyle(".checkbox-inverse-primary", ["--chkbg: var(--md-sys-color-inverse-primary);", "--chkfg: var(--md-sys-color-on-primary);"])
	// 	// Theming.addStyle(".checkbox-inverse-primary", ["--chkbg: var(--ip);", "--chkfg: var(--pc);", "outline-color:"])
	// 	// not working:
	// 	Theming.addStyle(".checkbox-inverse-primary:checked:focus-visible, .checkbox-inverse-primary[checked='true']:focus-visible, .checkbox-inverse-primary[aria-checked='true']:focus-visible", ["outline-color: var(--md-sys-color-inverse-primary);"])
	// })

	const colorTileClasses = 'h-full w-full p-2';
	const colorLabelClasses = 'text-left text-xs md:text-lg xl:text-xl';
</script>

<!-- // based on https://github.com/themeselection/flyonui/blob/bdbdaeec6b575b80283f5fda51abd3981a168fca/src/theming/index.js#L2
// match with Material Designs color palette
// export const flyonUIColorObject = {
//     transparent: 'transparent',
//     current: 'currentColor',

//     primary: '#794DFF',
//     'primary-content': '#794DFF',

//     secondary: 'var(--fallback-s,oklch(var(--s)/<alpha-value>))',
//     'secondary-content': 'var(--fallback-sc,oklch(var(--sc)/<alpha-value>))',

//     accent: 'var(--fallback-a,oklch(var(--a)/<alpha-value>))',
//     'accent-content': 'var(--fallback-ac,oklch(var(--ac)/<alpha-value>))',

//     neutral: 'var(--fallback-n,oklch(var(--n)/<alpha-value>))',
//     'neutral-content': 'var(--fallback-nc,oklch(var(--nc)/<alpha-value>))',

//     'base-100': 'var(--fallback-b1,oklch(var(--b1)/<alpha-value>))',
//     'base-200': 'var(--fallback-b2,oklch(var(--b2)/<alpha-value>))',
//     'base-300': 'var(--fallback-b3,oklch(var(--b3)/<alpha-value>))',
//     'base-content': 'var(--fallback-bc,oklch(var(--bc)/<alpha-value>))',

//     'base-shadow': 'var(--fallback-bs,oklch(var(--bs)/<alpha-value>))',

//     info: 'var(--fallback-in,oklch(var(--in)/<alpha-value>))',
//     'info-content': 'var(--fallback-inc,oklch(var(--inc)/<alpha-value>))',

//     success: 'var(--fallback-su,oklch(var(--su)/<alpha-value>))',
//     'success-content': 'var(--fallback-suc,oklch(var(--suc)/<alpha-value>))',

//     warning: 'var(--fallback-wa,oklch(var(--wa)/<alpha-value>))',
//     'warning-content': 'var(--fallback-wac,oklch(var(--wac)/<alpha-value>))',
//     error: 'var(--fallback-er,oklch(var(--er)/<alpha-value>))',

//     'error-content': 'var(--fallback-erc,oklch(var(--erc)/<alpha-value>))'
// } -->

<div class="w-full xl:grid xl:grid-cols-2 xl:gap-4">
	<div class="col-span-2">
		<Title>Colors</Title>
		<div class="flex items-center gap-1">
			<label class="label label-text text-base" for="switchColors">Hide</label>
			<input
				type="checkbox"
				class="switch switch-primary"
				bind:checked={showSections.colors}
				id="switchColors"
			/>
			<label class="label label-text text-base" for="switchColors">Show</label>
		</div>
		<div
			class="accordion accordion-bordered divide-y {showSections.colors ? '' : 'hidden'}"
			data-accordion-always-open=""
		>
			<!-- <div class="accordion-item accordion-item-active:scale-[1.05] accordion-item-active:mb-3 ease-in duration-300 delay-[1ms] active" id="default-colors"> -->
			<div class="active accordion-item" id="default-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="default-foreground-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">Default foreground colors FlyonUI</p>
				</button>
				<div
					id="default-foreground-colors-collapse"
					class="accordion-content w-full overflow-hidden transition-[height] duration-300"
					aria-labelledby="default-foreground-colors"
					role="region"
				>
					<div class="m-5 grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-8">
						<div>
							<ColorTileFlyonUi classes="bg-primary">
								<div class=" {colorTileClasses}">
									<p class="text-primary-content {colorLabelClasses}">primary</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-primary-content {colorTileClasses}">
									<p class="text-primary {colorLabelClasses}">primary-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-secondary {colorTileClasses}">
									<p class="text-secondary-content {colorLabelClasses}">secondary</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-secondary-content {colorTileClasses}">
									<p class="text-secondary {colorLabelClasses}">secondary-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-accent {colorTileClasses}">
									<p class="text-accent-content {colorLabelClasses}">accent</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-accent-content {colorTileClasses}">
									<p class="text-accent {colorLabelClasses}">accent-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-neutral {colorTileClasses}">
									<p class="text-neutral-content {colorLabelClasses}">neutral</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-neutral-content {colorTileClasses}">
									<p class="text-neutral {colorLabelClasses}">neutral-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-info {colorTileClasses}">
									<p class="text-info-content {colorLabelClasses}">info</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-info-content {colorTileClasses}">
									<p class="text-info {colorLabelClasses}">info-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-success {colorTileClasses}">
									<p class="text-success-content {colorLabelClasses}">success</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-success-content {colorTileClasses}">
									<p class="text-success {colorLabelClasses}">success-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-warning {colorTileClasses}">
									<p class="text-warning-content {colorLabelClasses}">warning</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-warning-content {colorTileClasses}">
									<p class="text-warning {colorLabelClasses}">warning-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-error {colorTileClasses}">
									<p class="text-error-content {colorLabelClasses}">error</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-error-content {colorTileClasses}">
									<p class="text-error {colorLabelClasses}">error-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
					</div>
				</div>

				<!-- <div>
                            <ColorTileFlyonUi background="primary" content="primary-content" />
                            <ColorTileFlyonUi background="primary-content" content="primary" />
                        </div> -->
				<!-- <div> -->
				<!-- <ColorTileFlyonUi background="secondary" content="secondary-content" /> -->
				<!-- <ColorTileFlyonUi background="secondary-content" content="secondary" /> -->
				<!-- Programmatically applied classes don't show up, unless they are references elsewhere in the DOM due to Svelte's tree-shaking -->
				<!-- <hr /> -->
				<!-- <div class="flex h-24 grow bg-secondary-content p-2">
                                <p class="text-left text-base text-secondary md:text-xl">secondary content direct</p>
                            </div>
                            <hr /> -->
				<!-- <ColorTileFlyonUi background="onSecondary" content="secondary" /> -->
				<!-- </div> -->
				<!-- <div>
                            <ColorTileFlyonUi background="accent" content="accent-content" />
							<div class="bg-accent">TEST</div>
                            <ColorTileFlyonUi background="accent-content" content="accent" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="neutral" content="neutral-content" />
                            <ColorTileFlyonUi background="neutral-content" content="neutral" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="info" content="info-content" />
                            <ColorTileFlyonUi background="info-content" content="info" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="success" content="success-content" />
                            <ColorTileFlyonUi background="success-content" content="success" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="warning" content="warning-content" />
                            <ColorTileFlyonUi background="warning-content" content="warning" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="error" content="error-content" />
                            <ColorTileFlyonUi background="error-content" content="error" />
                        </div> -->
				<!-- </div>
                </div> -->
			</div>
			<div class="active accordion-item" id="default-background-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="default-background-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">Default background colors FlyonU</p>
				</button>
				<div
					id="default-background-colors-collapse"
					class="accordion-content w-full overflow-hidden transition-[height] duration-300"
					aria-labelledby="default-background-colors"
					role="region"
				>
					<div class="m-5 grid grid-cols-2 gap-4 md:grid-cols-5">
						<ColorTileFlyonUi>
							<div class="bg-base-100 {colorTileClasses}">
								<p class={colorLabelClasses}>base-100</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-base-200 {colorTileClasses}">
								<p class={colorLabelClasses}>base-200</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-base-300 {colorTileClasses}">
								<p class={colorLabelClasses}>base-300</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-base-content {colorTileClasses}">
								<p class="text-secondary-content {colorLabelClasses}">base-content</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-base-shadow {colorTileClasses}">
								<p class="text-base-content {colorLabelClasses}">base-shadow</p>
							</div>
						</ColorTileFlyonUi>
						<!-- <ColorTileFlyonUi background="base-100" />
                        <ColorTileFlyonUi background="base-200" />
                        <ColorTileFlyonUi background="base-300" />
                        <ColorTileFlyonUi background="base-content" content="onSecondary" />
                        <ColorTileFlyonUi background="base-shadow" /> -->
						<!-- <div class="skeleton flex h-12 w-36 items-center justify-center bg-base-100">
                            <p class="text-center text-xl">base-100</p>
                        </div>
                        <div class="skeleton flex h-12 w-36 items-center justify-center bg-base-200">
                            <p class="text-center text-xl">base-200</p>
                        </div>
                        <div class="skeleton flex h-12 w-36 items-center justify-center bg-base-300">
                            <p class="text-center text-xl">base-300</p>
                        </div>
                        <div class="skeleton flex h-12 w-36 items-center justify-center bg-base-content">
                            <p class="text-center text-xl text-secondary-content">base-content</p>
                        </div>
                        <div class="skeleton flex h-12 w-36 items-center justify-center bg-base-shadow">
                            <p class="text-center text-xl text-base-content">base-shadow</p>
                        </div> -->
					</div>
				</div>
			</div>
			<div class="active accordion-item" id="opacity-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="opacity-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">Applying tailwind /x argument for opacity</p>
				</button>
				<div
					id="opacity-colors-collapse"
					class="accordion-content w-full overflow-hidden transition-[height] duration-300"
					aria-labelledby="opacity-colors"
					role="region"
				>
					<p class="ml-5">Primary:</p>
					<div class="m-5 grid grid-cols-4 gap-4 md:grid-cols-11">
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary">
							<p class="text-center text-xl"></p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/10">
							<p class="text-center text-xl">/10</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/20">
							<p class="text-center text-xl">/20</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/30">
							<p class="text-center text-xl">/30</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/40">
							<p class="text-center text-xl">/40</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/50">
							<p class="text-center text-xl">/50</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/60">
							<p class="text-center text-xl">/60</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/70">
							<p class="text-center text-xl">/70</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/80">
							<p class="text-center text-xl">/80</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/90">
							<p class="text-center text-xl">/90</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/100">
							<p class="text-center text-xl">/100</p>
						</div>
					</div>
					<p class="ml-5">Primary content:</p>
					<div class="m-5 grid grid-cols-4 gap-4 md:grid-cols-11">
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content">
							<p class="text-center text-xl"></p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/10">
							<p class="text-center text-xl">/10</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/20">
							<p class="text-center text-xl">/20</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/30">
							<p class="text-center text-xl">/30</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/40">
							<p class="text-center text-xl">/40</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/50">
							<p class="text-center text-xl">/50</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/60">
							<p class="text-center text-xl">/60</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/70">
							<p class="text-center text-xl">/70</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/80">
							<p class="text-center text-xl">/80</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/90">
							<p class="text-center text-xl">/90</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/100">
							<p class="text-center text-xl">/100</p>
						</div>
					</div>
					<p class="ml-5">Primary container - this is an extension from material UI to flyonUI:</p>
					<div class="m-5 grid grid-cols-4 gap-4 md:grid-cols-11">
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container">
							<p class="text-center text-xl"></p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/10">
							<p class="text-center text-xl">/10</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/20">
							<p class="text-center text-xl">/20</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/30">
							<p class="text-center text-xl">/30</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/40">
							<p class="text-center text-xl">/40</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/50">
							<p class="text-center text-xl">/50</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/60">
							<p class="text-center text-xl">/60</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/70">
							<p class="text-center text-xl">/70</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/80">
							<p class="text-center text-xl">/80</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/90">
							<p class="text-center text-xl">/90</p>
						</div>
						<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container/100">
							<p class="text-center text-xl">/100</p>
						</div>
						<!-- Programmatically applying for the first time doesn't work - if it's the only applying of this color.
						But once applied there is some caching on the server side - shared between clients. -->
						<!-- {#each ["/10", "/20", "/30", "/40", "/50", "/60", "/70", "/80", "/90", "/100"] as opacity}
							<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-container{opacity}">
								<p class="text-center text-xl">{opacity}</p>
							</div>
						{/each} -->
					</div>
				</div>
			</div>
			<div class="active accordion-item" id="extension-materialui-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="extension-materialui-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">
						Extensions for foreground to FlyonUI with extra Material UI colors
					</p>
				</button>
				<div
					id="extension-materialui-colors-collapse"
					class="accordion-content w-full overflow-hidden transition-[height] duration-300"
					aria-labelledby="extension-materialui-colors"
					role="region"
				>
					<div class="m-5 grid grid-cols-4 gap-4 xl:grid-cols-8">
						<div>
							<ColorTileFlyonUi>
								<div class="bg-primary-container {colorTileClasses}">
									<p class="text-primary-container-content {colorLabelClasses}">
										primary-container
									</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-primary-container-content {colorTileClasses}">
									<p class="text-primary-container {colorLabelClasses}">
										primary-container-content
									</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-secondary-container {colorTileClasses}">
									<p class="text-secondary-container-content {colorLabelClasses}">
										secondary-container
									</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-secondary-container-content {colorTileClasses}">
									<p class="text-secondary-container {colorLabelClasses}">
										secondary-container-content
									</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-accent-container {colorTileClasses}">
									<p class="text-accent-container-content {colorLabelClasses}">accent-container</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-accent-container-content {colorTileClasses}">
									<p class="text-accent-container {colorLabelClasses}">accent-container-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-neutral-container {colorTileClasses}">
									<p class="text-neutral-container-content {colorLabelClasses}">
										neutral-container
									</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-neutral-container-content {colorTileClasses}">
									<p class="text-neutral-container {colorLabelClasses}">
										neutral-container-content
									</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-info-container {colorTileClasses}">
									<p class="text-info-container-content {colorLabelClasses}">info-container</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-info-container-content {colorTileClasses}">
									<p class="text-info-container {colorLabelClasses}">info-container-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-success-container {colorTileClasses}">
									<p class="text-success-container-content {colorLabelClasses}">
										success-container
									</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-success-container-content {colorTileClasses}">
									<p class="text-success-container {colorLabelClasses}">
										success-container-content
									</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-warning-container {colorTileClasses}">
									<p class="text-warning-container-content {colorLabelClasses}">
										warning-container
									</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-warning-container-content {colorTileClasses}">
									<p class="text-warning-container {colorLabelClasses}">
										warning-container-content
									</p>
								</div>
							</ColorTileFlyonUi>
						</div>
						<div>
							<ColorTileFlyonUi>
								<div class="bg-error-container {colorTileClasses}">
									<p class="text-error-container-content {colorLabelClasses}">error-container</p>
								</div>
							</ColorTileFlyonUi>
							<ColorTileFlyonUi>
								<div class="bg-error-container-content {colorTileClasses}">
									<p class="text-error-container {colorLabelClasses}">error-container-content</p>
								</div>
							</ColorTileFlyonUi>
						</div>
					</div>
				</div>
			</div>
			<div class="active accordion-item" id="extension-materialui-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="extension-background-materialui-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">
						Extensions for background to FlyonUI with extra Material UI colors
					</p>
				</button>
				<div
					id="extension-background-materialui-colors-collapse"
					class="accordion-content w-full overflow-hidden transition-[height] duration-300"
					aria-labelledby="extension-background-materialui-colors"
					role="region"
				>
					<div class="m-5 grid grid-cols-4 gap-4 xl:grid-cols-8">
						<ColorTileFlyonUi>
							<div class="bg-base-50 {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">base-50</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-base-150 {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">base-150</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-outline {colorTileClasses}">
								<p class="text-inverse-surface-content {colorLabelClasses}">outline</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-outline-variant {colorTileClasses}">
								<p class="text-inverse-surface-content {colorLabelClasses}">outline-variant</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-inverse-surface {colorTileClasses}">
								<p class="text-inverse-surface-content {colorLabelClasses}">inverse-surface</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-inverse-surface-content {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">inverse-surface-content</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-inverse-primary {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">inverse-primary</p>
							</div>
						</ColorTileFlyonUi>
					</div>
					<div class="m-5 grid grid-cols-2 gap-4 md:grid-cols-3">
						<ColorTileFlyonUi>
							<div class="bg-scrim {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">scrim</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-background {colorTileClasses}">
								<p class="text-background-content {colorLabelClasses}">background</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-background-content {colorTileClasses}">
								<p class="text-background {colorLabelClasses}">background-content</p>
							</div>
						</ColorTileFlyonUi>
					</div>
					<div class="m-5 grid grid-cols-2 gap-4 md:grid-cols-5">
						<ColorTileFlyonUi>
							<div class="bg-neutral-palette-key-color {colorTileClasses}">
								<p class="text-inverse-surface-content {colorLabelClasses}">neutral-palette-key</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-neutral-variant-palette-key-color {colorTileClasses}">
								<p class="text-inverse-surface-content {colorLabelClasses}">
									neutral-variant-palette-key
								</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-primary-palette-key-color {colorTileClasses}">
								<p class="text-background-content {colorLabelClasses}">primary-palette-key</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-secondary-palette-key-color {colorTileClasses}">
								<p class="text-background {colorLabelClasses}">secondary-palette-key</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-accent-palette-key-color {colorTileClasses}">
								<p class="text-inverse-surface-content {colorLabelClasses}">accent-palette-key</p>
							</div>
						</ColorTileFlyonUi>

						<p class="text-2xl">TBD: Others: background and more</p>
						<div>surface container low - between b1 and b2</div>
						<div>surface container high - between b2 and b3</div>
						<div>on surface variant</div>
						<div>outline</div>
						<div>outline variant</div>
						<div>inverse surface</div>
						<div>inverse on surface</div>
						<div>inverse primary</div>
						<div>scrim</div>
						<div>background - might not be necessary?</div>
						<div>on background</div>
						<div>
							neutral palette key color - not the neutral from above, as the color input is coming
							from flyonUI, but this one is material designs own
						</div>
						<div>neutral variant palette key color</div>
					</div>
				</div>
			</div>
			<div class="active accordion-item" id="avoid-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="avoid-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">
						Avoid using those extensions FlyonUI with extra Material UI colors
					</p>
				</button>
				<div
					id="avoid-colors-collapse"
					class="accordion-content w-full overflow-hidden transition-[height] duration-300"
					aria-labelledby="avoid-materialui-colors"
					role="region"
				>
					<div class="m-5 grid grid-cols-4 gap-4">
						<ColorTileFlyonUi>
							<div class="bg-primary-fixed {colorTileClasses}">
								<p class="text-primary-fixed-content {colorLabelClasses}">primary-fixed</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-primary-fixed-dim {colorTileClasses}">
								<p class="text-primary-fixed-content {colorLabelClasses}">primary-fixed-dim</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-primary-fixed-content {colorTileClasses}">
								<p class="text-primary-fixed {colorLabelClasses}">primary-fixed-content</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-primary-fixed-variant-content {colorTileClasses}">
								<p class="text-primary-fixed {colorLabelClasses}">primary-fixed-variant-content</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-secondary-fixed {colorTileClasses}">
								<p class="text-secondary-fixed-content {colorLabelClasses}">secondary-fixed</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-secondary-fixed-dim {colorTileClasses}">
								<p class="text-secondary-fixed-content {colorLabelClasses}">secondary-fixed-dim</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-secondary-fixed-content {colorTileClasses}">
								<p class="text-secondary-fixed {colorLabelClasses}">secondary-fixed-content</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-secondary-fixed-variant-content {colorTileClasses}">
								<p class="text-secondary-fixed {colorLabelClasses}">
									secondary-fixed-variant-content
								</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-accent-fixed {colorTileClasses}">
								<p class="text-accent-fixed-content {colorLabelClasses}">accent-fixed</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-accent-fixed-dim {colorTileClasses}">
								<p class="text-accent-fixed-content {colorLabelClasses}">accent-fixed-dim</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-accent-fixed-content {colorTileClasses}">
								<p class="text-accent-fixed {colorLabelClasses}">accent-fixed-content</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-accent-fixed-variant-content {colorTileClasses}">
								<p class="text-accent-fixed {colorLabelClasses}">accent-fixed-variant-content</p>
							</div>
						</ColorTileFlyonUi>
					</div>
					<div class="m-5 grid grid-cols-5 gap-4 xl:grid-cols-8">
						<ColorTileFlyonUi>
							<div class="bg-surface-dim {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">surface-dim</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-surface {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">surface</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-surface-bright {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">surface-bright</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-surface-variant {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">surface-variant</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-surface-tint {colorTileClasses}">
								<p class="text-inverse-surface-content {colorLabelClasses}">surface-tint</p>
							</div>
						</ColorTileFlyonUi>

						<p class="text-2xl">
							Avoid the following - fixed is not switching between light and dark
						</p>
						<div>primary fixed</div>
						<div>primary variant dim</div>
						<div>on primary variant</div>
						<div>on primary fixed variant</div>
						<div>secondary fixed</div>
						<div>secondary fixed dim</div>
						<div>on secondary fixed</div>
						<div>on secondary fixed variant</div>
						<div>tertiary fixed</div>
						<div>tertiary fixed dim</div>
						<div>on tertiary fixed</div>
						<div>on tertiary fixed variant</div>
						<div>surface dim</div>
						<div>surface</div>
						<div>surface bright</div>
						<div>surface variant</div>
						<div>surface tint</div>
					</div>
				</div>
			</div>
			<div class="active accordion-item" id="aliases-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="aliases-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] size-5 shrink-0 transition-transform duration-300 accordion-item-active:rotate-90 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">
						TBD: remove! no extra style sheets! Aliases: material design - flyonui: same color,
						different utility class names
					</p>
				</button>
				<div
					id="aliases-colors-collapse"
					class="accordion-content w-full overflow-hidden transition-[height] duration-300"
					aria-labelledby="aliases-colors"
					role="region"
				>
					<div class="m-5 grid grid-cols-4 gap-4 xl:grid-cols-8"></div>
				</div>
			</div>
		</div>
		<div class="col-span-2">
			<p class="text-xl italic">
				Note, for programmatically applied classes, add the utility class either programmatically
				via <code>Theming.addStyle( styleName, styles)</code>
				or as (scoped) <code>&ltstyle&gt</code> tag.
			</p>
		</div>
	</div>

	<div class="col-span-2">
		<Title>Utility classes</Title>
		<div class="flex items-center gap-1">
			<label class="label label-text text-base" for="switchColors">Hide</label>
			<input
				type="checkbox"
				class="switch switch-primary"
				bind:checked={showSections.utilityClasses}
				id="switchColors"
			/>
			<label class="label label-text text-base" for="switchColors">Show</label>
		</div>
		<div class={showSections.utilityClasses ? '' : 'hidden'}>
			Mainly playing with:
			<ul>
				<li>primary (native in both FlyonUI and Material Design),</li>
				<li>inverse primary (native only in Material Design),</li>
				<li>surface tint (avoid using),</li>
				<li>error (also native in both - showing it works)</li>
				<li>error/50 (checking transparency from Tailwind)</li>
			</ul>
		</div>
		<div class="mt-5 grid grid-cols-5 gap-4 {showSections.utilityClasses ? '' : 'hidden'}">
			<div class="col-span-5 ml-5 text-2xl font-semibold">bg-"COLOR-NAME"</div>
			<div class="h-24 bg-primary">bg-primary</div>
			<div class="bg-inverse-primary h-24">bg-inverse-primary</div>
			<div class="bg-surface-tint h-24">bg-surface-tint</div>
			<div class="h-24 bg-error">bg-error</div>
			<div class="h-24 bg-error/50">bg-error/50</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">
				from-"COLOR-NAME" via-"COLOR-NAME" to-"COLOR-NAME"
			</div>
			<div class="h-24 bg-gradient-to-r from-primary via-secondary to-accent">
				from-primary via-scondary to-accent
			</div>
			<div class="h-24 bg-gradient-to-r from-success via-warning to-error">
				from-success via-warning to-error
			</div>
			<div
				class="h-24 w-fit bg-gradient-to-r from-success via-warning to-error bg-clip-text text-xl font-black text-transparent"
			>
				from-success via-warning to-error applied to text
			</div>
			<div class="via-inverse-primary to-surface-tint h-24 bg-gradient-to-r from-primary">
				from-primary via-inverse-primary to-surface-tint
			</div>
			<div class="h-24 bg-gradient-to-r from-primary/50 via-secondary/50 to-accent/50">
				from-primary/50 via-scondary/50 to-accent/50
			</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">text-"COLOR-NAME"</div>
			<div class="h-24 text-xl font-bold text-primary md:text-3xl">text-primary</div>
			<div class="text-inverse-primary h-24 text-xl font-bold md:text-3xl">
				text-inverse-primary
			</div>
			<div class="text-surface-tint h-24 text-xl font-bold md:text-3xl">text-surface-tint</div>
			<div class="h-24 text-xl font-bold text-error md:text-3xl">text-error</div>
			<div class="h-24 text-xl font-bold text-error/50 md:text-3xl">text-error/50</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">ring-"COLOR-NAME"</div>
			<div>
				<input
					type="radio"
					name="radioPrimary"
					class="radio radio-primary"
					id="radioPrimary"
					checked
				/>Radio primary
			</div>
			<div>
				<input
					type="radio"
					name="radioInversePrimary"
					class="radio-inverse-primary radio"
					id="radioInversePrimary"
					checked
				/>Radio inverse primary
			</div>
			<div>
				<input
					type="radio"
					name="radioSurfaceTint"
					class="radio-surface-tint radio"
					id="radioSurfaceTint"
					checked
				/>Radio surface tint
			</div>
			<div>
				<input
					type="radio"
					name="radioError"
					class="radio radio-error"
					id="radioError"
					checked
				/>Radio error
			</div>
			<div>
				<input
					type="radio"
					name="radioError50"
					class="radio-error/50 radio"
					id="radioError50"
					checked
				/>Radio error/50
			</div>
			<button class="button ring ring-primary">ring-primary</button>
			<button class="button ring-inverse-primary ring">ring-inverse-primary</button>
			<button class="button ring-surface-tint ring">ring-surface-tint</button>
			<button class="button ring ring-error">ring-error</button>
			<button class="button ring ring-error/50">ring-error/50</button>

			<div class="col-span-5 ml-5 text-2xl font-semibold">fill-"COLOR-NAME"</div>
			<svg class="h-14 fill-primary" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"
				><path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"
				></path></svg
			>
			<svg class="fill-inverse-primary h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"
				><path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"
				></path></svg
			>
			<svg class="fill-surface-tint h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"
				><path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"
				></path></svg
			>
			<svg class="h-14 fill-error" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"
				><path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"
				></path></svg
			>
			<svg class="h-14 fill-error/50" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"
				><path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"
				></path></svg
			>

			<div class="col-span-5 ml-5 text-2xl font-semibold">caret-"COLOR-NAME"</div>
			<textarea class="h-24 caret-primary">caret-primary: cursor color!</textarea>
			<textarea class="caret-inverse-primary h-24">caret-inverse-primary: cursor color!</textarea>
			<textarea class="caret-surface-tint h-24">caret-surface-tint: cursor color!</textarea>
			<textarea class="h-24 caret-error">caret-error: cursor color!</textarea>
			<textarea class="h-24 caret-error/50">caret-error/50: cursor color!</textarea>

			<div class="col-span-5 ml-5 text-2xl font-semibold">stroke-"COLOR-NAME"</div>
			<svg
				class="h-10 stroke-primary"
				viewBox="0 0 48 40"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z"
					stroke-width="2"
				></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>
			<svg
				class="stroke-inverse-primary h-10"
				viewBox="0 0 48 40"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z"
					stroke-width="2"
				></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>
			<svg
				class="stroke-surface-tint h-10"
				viewBox="0 0 48 40"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z"
					stroke-width="2"
				></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>
			<svg
				class="h-10 stroke-error"
				viewBox="0 0 48 40"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z"
					stroke-width="2"
				></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>
			<svg
				class="h-10 stroke-error/50"
				viewBox="0 0 48 40"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z"
					stroke-width="2"
				></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>

			<div class="col-span-5 ml-5 text-2xl font-semibold">border-"COLOR-NAME"</div>
			<div class="h-24 border-4 border-primary">border-primary</div>
			<div class="border-inverse-primary h-24 border-4">border-inverse-primary</div>
			<div class="border-surface-tint h-24 border-4">border-surface-tint</div>
			<div class="h-24 border-4 border-error">border-error</div>
			<div class="h-24 border-4 border-error/50">border-error/50</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">divide-"COLOR-NAME"</div>
			<div class="h-24 divide-y divide-primary">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>
			<div class="divide-inverse-primary h-24 divide-y">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>
			<div class="divide-surface-tint h-24 divide-y">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>
			<div class="h-24 divide-y divide-error">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>
			<div class="h-24 divide-y divide-error/50">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">accent-"COLOR-NAME"</div>
			<label>
				<input type="checkbox" class="accent-primary" checked /> primary
			</label>
			<label>
				<input type="checkbox" class="accent-inverse-primary" checked /> inverse primary
			</label>
			<label>
				<input type="checkbox" class="accent-surface-tint" checked /> surface tint
			</label>
			<label>
				<input type="checkbox" class="accent-error" checked /> error
			</label>
			<label>
				<input type="checkbox" class="accent-error/50" checked /> error/50
			</label>
			<label>
				<input type="checkbox" class="checkbox checkbox-primary" checked /> primary
			</label>
			<label>
				<input type="checkbox" class="checkbox-inverse-primary checkbox" checked /> inverse primary
			</label>
			<label>
				<input type="checkbox" class="checkbox-surface-tint checkbox" checked /> surface tint
			</label>
			<label>
				<input type="checkbox" class="checkbox checkbox-error" checked /> error
			</label>
			<label>
				<input type="checkbox" class="checkbox-error/50 checkbox" checked /> error/50
			</label>

			<div class="col-span-5 ml-5 text-2xl font-semibold">shadow-"COLOR-NAME"</div>
			<button class="btn btn-primary shadow-lg shadow-primary">Shadow primary</button>
			<button class="btn btn-inverse-primary shadow-inverse-primary shadow-lg"
				>Shadow inverse primary</button
			>
			<button class="btn-surface-tint shadow-surface-tint btn shadow-lg">Shadow surface tint</button
			>
			<button class="btn btn-error shadow-lg shadow-error">Shadow error</button>
			<button class="btn-error/50 btn shadow-lg shadow-error/50">Shadow error/50</button>

			<div class="col-span-5 ml-5 text-2xl font-semibold">outline-"COLOR-NAME"</div>
			<button class="btn btn-primary btn-outline">primary</button>
			<button class="btn btn-inverse-primary btn-outline">inverse primary</button>
			<button class="btn-surface-tint btn btn-outline">surface tint</button>
			<button class="btn btn-error btn-outline">error</button>
			<button class="btn-error/50 btn btn-outline">error/50</button>
			<div class="items-center gap-1">
				<input
					type="checkbox"
					class="switch switch-primary switch-outline"
					id="switchPrimary"
					checked
				/>
				<label class="label label-text text-base" for="switchPrimary"> Default </label>
			</div>
			<div class="items-center gap-1">
				<input
					type="checkbox"
					class="switch-inverse-primary switch switch-outline"
					id="switchInversePrimary"
					checked
				/>
				<label class="label label-text text-base" for="switchInversePrimary"> Inverse </label>
			</div>
			<div class="items-center gap-1">
				<input
					type="checkbox"
					class="switch-surface-tint switch switch-outline"
					id="switchSurfaceTint"
					checked
				/>
				<label class="label label-text text-base" for="switchSurfaceTint"> Surface tint </label>
			</div>
			<div class="items-center gap-1">
				<input
					type="checkbox"
					class="switch switch-error switch-outline"
					id="switchError"
					checked
				/>
				<label class="label label-text text-base" for="switchError"> Error </label>
			</div>
			<div class="items-center gap-1">
				<input
					type="checkbox"
					class="switch-error/50 switch switch-outline"
					id="switchError50"
					checked
				/>
				<label class="label label-text text-base" for="switchError50"> Error/50 </label>
			</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">decoration-"COLOR-NAME"</div>
			<div class="h-24 underline decoration-primary">decoration-primary</div>
			<div class="decoration-inverse-primary h-24 underline">decoration-inverse-primary</div>
			<div class="decoration-surface-tint h-24 underline">decoration-surface-tint</div>
			<div class="h-24 underline decoration-error">decoration-error</div>
			<div class="h-24 underline decoration-error/50">decoration-error/50</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">placeholder-"COLOR-NAME"</div>
			<label class="relative block">
				<input
					class="input placeholder:text-primary"
					placeholder="Placeholder primary"
					type="text"
					name="search"
				/>
			</label>
			<label class="relative block">
				<input
					class="placeholder:text-inverse-primary input"
					placeholder="Placeholder inverse primary"
					type="text"
					name="search"
				/>
			</label>
			<label class="relative block">
				<input
					class="placeholder:text-surface-tint input"
					placeholder="Placeholder surface tint"
					type="text"
					name="search"
				/>
			</label>
			<label class="relative block">
				<input
					class="input placeholder:text-error"
					placeholder="Placeholder error"
					type="text"
					name="search"
				/>
			</label>
			<label class="relative block">
				<input
					class="input placeholder:text-error/50"
					placeholder="Placeholder error/50"
					type="text"
					name="search"
				/>
			</label>

			<div class="col-span-5 ml-5 text-2xl font-semibold">ring-offset-"COLOR-NAME"</div>
			<span
				class="badge col-span-5 ring-2 ring-red-300 ring-offset-4 ring-offset-primary md:col-span-1"
				>primary</span
			>
			<span
				class="ring-offset-inverse-primary badge col-span-5 ring-2 ring-red-300 ring-offset-4 md:col-span-1"
				>inverse primary</span
			>
			<span
				class="ring-offset-surface-tint badge col-span-5 ring-2 ring-red-300 ring-offset-4 md:col-span-1"
				>surface tint</span
			>
			<span
				class="badge col-span-5 ring-2 ring-blue-300 ring-offset-4 ring-offset-error md:col-span-1"
				>error</span
			>
			<span
				class="badge col-span-5 ring-2 ring-blue-300 ring-offset-4 ring-offset-error/50 md:col-span-1"
				>error/50</span
			>
		</div>
	</div>

	<div>
		<Title>Components with utility classes</Title>
		<p>Badges:</p>
		<span class="badge badge-primary">Badge primary</span>
		<span class="badge badge-secondary">Badge secondary</span>
		<span class="badge badge-accent">Badge accent</span>
		<span class="badge badge-inverse-primary">Badge inverse primary</span>
		<br />
		<p>Glass effect on button:</p>
		<button class="btn btn-primary glass ">Glass on primary</button>
		<button class="btn btn-inverse-primary glass">Glass on inverse primary</button>
		<button class="btn btn-surface-tint  glass">Glass on surface tint</button>
		<button class="btn btn-error glass">Glass on error</button>
		<button class="btn btn-error/50 glass">Glass on error/50</button>
		<p>Using postCSS created components:</p>
		<span class="badge badge-primary-container">Badge primary-container</span>
	</div>

	<div>
		<Title>Typography</Title>
		<link rel="preconnect" href="https://fonts.googleapis.com" />
		<p>Fonts:</p>
		<p class="font-sans">
			Some text in <em>sans</em> font family, should be using <b>Robot</b> Google Fonts extending
			default theme in <code>tailwindcss.config.js</code>.
		</p>
		<p class="font-serif">
			Some text in <em>serif</em> font family, should be using <b>Merriweather</b> Google Fonts,
			extending default theme in <code>tailwindcss.config.js</code>.
		</p>
		<p class="font-mono">
			Some text in <em>mono</em> font family, still <b>TailwindCSS</b> default, not overwritten in
			<code>tailwindcss.config.js</code> yet
		</p>
	</div>

	<div>
		<Title>Styles</Title>
		Targets with their default values:
		<ul>
			<li>--rounded-box: 0.5rem ;</li>
			<li>--rounded-btn: 0.375rem;</li>
			<li>--rounded-tooltip: 0.25rem;</li>
			<li>--animation-btn: 0.25s;</li>
			<li>--animation-input: .2s;</li>
			<li>--btn-focus-scale: 0.95;</li>
			<li>--border-btn: 1px;</li>
			<li>--tab-border: 1px;</li>
			<li>--tab-radius: 0.5rem;</li>
		</ul>
	</div>

	<div>
		<Title>Icons</Title>
		<p class="text-center text-xl">Iconify with FlyonUI</p>
		<div class="grid grid-cols-5 gap-4">
			<div>
				<p class="text-center text-xl">Default library "tablers"</p>
				<span class="icon-[tabler--settings] size-12"></span>
				<span class="icon-[tabler--palette] size-12"></span>
				<span class="icon-[tabler--home] size-12"></span>
				<span class="icon-[tabler--user] size-12"></span>
			</div>
			<div>
				<p class="text-center text-xl">Extension library "Material Symbols"</p>
				<span class="icon-[material-symbols--settings-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--palette-outline] size-12"></span>
				<span class="icon-[material-symbols--home-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--person-outline-rounded] size-12"></span>
			</div>
			<div>
				<p class="text-center text-xl">Extension library "SVG spinners"</p>
				<span class="icon-[svg-spinners--12-dots-scale-rotate] size-12"></span>
				<span class="icon-[svg-spinners--3-dots-bounce] size-12"></span>
				<span class="icon-[svg-spinners--6-dots-rotate] size-12"></span>
				<span class="icon-[svg-spinners--90-ring-with-bg] size-12"></span>
				<span class="icon-[svg-spinners--clock] size-12"></span>
				<span class="icon-[svg-spinners--bars-scale] size-12"></span>
				<span class="icon-[svg-spinners--wifi] size-12"></span>
				<span class="icon-[svg-spinners--wifi-fade] size-12"></span>
			</div>
			<div>
				<p class="text-center text-xl">Extension library "Font Awesome Solid</p>
				<span class="icon-[fa6-solid--droplet] size-12"></span>
				<span class="icon-[fa6-solid--comments] size-12"></span>
				<p class="text-center text-xl">Extension library "Font Awesome Brands</p>
				<span class="icon-[fa6-brands--discord] size-12"></span>
				<span class="icon-[fa6-brands--youtube] size-12"></span>
				<span class="icon-[fa6-brands--linux] size-12"></span>
				<span class="icon-[fa6-brands--github] size-12"></span>
			</div>
			<div>
				<p class="text-center text-xl">Extension library "Noto emoji</p>
				<span class="icon-[noto--folded-hands] size-12"></span>
				<span class="icon-[noto--folded-hands-medium-dark-skin-tone] size-12"></span>
				<span class="icon-[noto--heart-hands] size-12"></span>
				<span class="icon-[noto--heart-hands-dark-skin-tone] size-12"></span>
				<span class="icon-[noto--fire] size-12"></span>
				<span class="icon-[noto--smiling-face-with-sunglasses] size-12"></span>
				<span class="icon-[noto--check-mark-button] size-12"></span>
				<span class="icon-[noto--cross-mark] size-12"></span>
			</div>
		</div>
	</div>

	<div>
		<Title>Theme Picker</Title>
		<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
			<div class="w-48">
				<label class="label label-text" for="colorPicker"
					>Source color
					<span class="label">
						<code class="label-text-alt">{sourceColor}</code>
					</span>
				</label>
				<input
					class="w-full"
					type="color"
					id="colorPicker"
					name="color-picker"
					bind:value={sourceColor}
				/>
			</div>
			<div class="relative w-48">
				<label class="label label-text" for="themeVariant">Variant</label>
				<select
					class="select select-floating max-w-sm"
					aria-label="Select variant"
					id="themeVariant"
					bind:value={variant}
				>
					<option value="TONAL_SPOT">Tonal Spot</option>
					<option value="MONOCHROME">Monochrome</option>
					<option value="NEUTRAL">Neutral</option>
					<option value="VIBRANT">Vibrant</option>
					<option value="EXPRESSIVE">Expressive</option>
					<option value="FIDELITY">Fidelity</option>
					<option value="CONTENT">Content</option>
					<option value="RAINBOW">Rainbow</option>
					<option value="FRUIT_SALAD">Fruit Salad</option>
				</select>
			</div>
			<div class="w-48">
				<label class="label label-text" for="contrast"
					>Contrast: <span class="label">
						<code class="label-text-alt">{contrast}</code>
					</span></label
				>

				<input
					type="range"
					min={contrastMin}
					max={contrastMax}
					step={contrastStep}
					class="range w-full"
					aria-label="contrast"
					id="contrast"
					bind:value={contrast}
				/>
				<div class="flex w-full justify-between px-2 text-xs">
					{#each allContrasts as _}
						<span>|</span>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<div>
		<Title>Modal</Title>
		<button
			type="button"
			class="btn btn-accent"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="basic-modal"
			data-overlay="#basic-modal"
			onclick={openModal}
		>
			Open modal
		</button>

		<!-- <div bind:this={modal} id="basic-modal" class="overlay modal overlay-open:opacity-100 hidden" role="dialog" tabindex="-1"> -->
		<div
			bind:this={myModal}
			id="basic-modal"
			class="overlay modal hidden overlay-open:opacity-100"
			role="dialog"
			tabindex="-1"
		>
			<div class="modal-dialog overlay-open:opacity-100">
				<div class="modal-content bg-base-300">
					<div class="modal-header">
						<h3 class="modal-title">Dialog Title</h3>
						<button
							type="button"
							class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
							aria-label="Close"
							data-overlay="#basic-modal"
						>
							<span class="icon-[tabler--x] size-4"></span>
						</button>
					</div>
					<div class="modal-body">
						This is some placeholder content to show the scrolling behavior for modals. Instead of
						repeating the text in the modal, we use an inline style to set a minimum height, thereby
						extending the length of the overall modal and demonstrating the overflow scrolling. When
						content becomes longer than the height of the viewport, scrolling will move the modal as
						needed.
					</div>
					<div class="modal-footer">
						<button type="button" class="btn btn-secondary btn-soft" data-overlay="#basic-modal"
							>Close</button
						>
						<button type="button" class="btn btn-primary">Save changes</button>
					</div>
				</div>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<div>
		<Title>Swaps</Title>
		<div class="grid grid-cols-12 gap-4">
			<div>
				<label class="swap">
					<input type="checkbox" />
					<span class="icon-[tabler--volume] swap-on size-6"></span>
					<span class="icon-[tabler--volume-off] swap-off size-6"></span>
				</label>
			</div>
			<div>
				<label class="btn btn-circle swap swap-rotate">
					<input type="checkbox" />
					<span class="icon-[tabler--menu-2] swap-off"></span>
					<span class="icon-[tabler--x] swap-on"></span>
				</label>
			</div>
			<div>
				<label class="swap swap-rotate">
					<input type="checkbox" />
					<span class="icon-[tabler--sun] swap-on size-6"></span>
					<span class="icon-[tabler--moon] swap-off size-6"></span>
				</label>
			</div>
			<div>
				<label class="swap swap-flip text-6xl">
					<input type="checkbox" />
					<span class="swap-on">😈</span>
					<span class="swap-off">😇</span>
				</label>
			</div>
			<!-- <div>
                <label bind:this={myTemperature} class="swap swap-js text-6xl">
                    <span class="swap-on">🥵</span>
                    <span class="swap-off">🥶</span>
                </label>
                <label class="swap swap-js text-6xl">
                    <span class="swap-on">🥳</span>
                    <span class="swap-off">😭</span>
                </label>
            </div> -->
			<div>
				<label class="btn btn-circle swap swap-rotate">
					<input type="checkbox" />
					<span class="icon-[tabler--player-play] swap-off"></span>
					<span class="icon-[tabler--player-pause] swap-on"></span>
				</label>
			</div>
		</div>

		<HorizontalRule />
	</div>

	<!-- This local override works:
    style="background-color: var(--my-color); color: var(--md-sys-color-on-primary);" -->
	<div>
		<Title>Drawer (Sidebar)</Title>
		<button
			type="button"
			class="btn btn-primary"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="overlay-example"
			data-overlay="#overlay-example">Open drawer</button
		>

		<div
			id="overlay-example"
			class="overlay drawer drawer-start hidden overlay-open:translate-x-0"
			role="dialog"
			tabindex="-1"
		>
			<div class="drawer-header">
				<h3 class="drawer-title">Drawer Title</h3>
				<button
					type="button"
					class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
					aria-label="Close"
					data-overlay="#overlay-example"
				>
					<span class="icon-[tabler--x] size-5"></span>
				</button>
			</div>
			<div class="drawer-body">
				<p>
					Some text as placeholder. In real life you can have the elements you have chosen. Like,
					text, images, lists, etc.
				</p>
			</div>
			<div class="drawer-footer">
				<button type="button" class="btn btn-secondary btn-soft" data-overlay="#overlay-example"
					>Close</button
				>
				<button type="button" class="btn btn-primary">Save changes</button>
			</div>
		</div>

		<HorizontalRule />
	</div>

	<div>
		<Title>Card</Title>
		<div class="card sm:max-w-sm">
			<div class="card-body">
				<h5 class="card-title mb-2.5">Body of a Card here</h5>
				<p class="mb-4">
					Soe text to fill in the body fo the card. This could be anything here. But for now just
					text filling in here.
				</p>
				<div class="card-actions">
					<button class="btn btn-primary">Card button</button>
				</div>
			</div>
		</div>
	</div>

	<!-- <div>
        <Title>Menus</Title>
        <div class="grid grid-cols-6 gap-4">
            <div>
                <ul class="menu w-64 space-y-0.5 [&_.nested-collapse-wrapper]:space-y-0.5 [&_ul]:space-y-0.5">
                    <li>
                    <a href="#">
                        <span class="icon-[tabler--home] size-5"></span>
                        Home
                    </a>
                    </li>
                    <li class="space-y-0.5">
                    <a class="collapse-toggle collapse-open:bg-primary-content/10 open" id="menu-app" data-collapse="#menu-app-collapse">
                        <span class="icon-[tabler--apps] size-5"></span>
                        Apps
                        <span class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"></span>
                    </a>
                    <ul id="menu-app-collapse" class="open collapse w-auto overflow-hidden transition-[height] duration-300" aria-labelledby="menu-app">
                        <li>
                        <a href="#">
                            <span class="icon-[tabler--message] size-5"></span>
                            Chat
                        </a>
                        </li>
                        <li>
                        <a href="#">
                            <span class="icon-[tabler--calendar] size-5"></span>
                            Calendar
                        </a>
                        </li>
                        <li class="nested-collapse-wrapper">
                        <a class="collapse-toggle nested-collapse open" id="sub-menu-academy" data-collapse="#sub-menu-academy-collapse">
                            <span class="icon-[tabler--book] size-5"></span>
                            Academy
                            <span class="icon-[tabler--chevron-down] collapse-icon size-4"></span>
                        </a>
                        <ul id="sub-menu-academy-collapse" class="open collapse w-auto overflow-hidden transition-[height] duration-300" aria-labelledby="sub-menu-academy">
                            <li>
                            <a href="#">
                                <span class="icon-[tabler--books] size-5"></span>
                                Courses
                            </a>
                            </li>
                            <li>
                            <a href="#">
                                <span class="icon-[tabler--list-details] size-5"></span>
                                Course details
                            </a>
                            </li>
                            <li class="nested-collapse-wrapper">
                            <a class="collapse-toggle nested-collapse open" id="sub-menu-academy-stats" data-collapse="#sub-menu-academy-stats-collapse">
                                <span class="icon-[tabler--chart-bar] size-5"></span>
                                Stats
                                <span class="icon-[tabler--chevron-down] collapse-icon size-4"></span>
                            </a>
                            <ul id="sub-menu-academy-stats-collapse" class="open collapse w-auto overflow-hidden transition-[height] duration-300" aria-labelledby="sub-menu-academy-stats">
                                <li>
                                <a href="#">
                                    <span class="icon-[tabler--chart-donut] size-5"></span>
                                    Goals
                                </a>
                                </li>
                            </ul>
                            </li>
                        </ul>
                        </li>
                    </ul>
                    </li>
                    <li>
                    <a href="#">
                        <span class="icon-[tabler--settings] size-5"></span>
                        Settings
                    </a>
                    </li>
                </ul>
            </div>
        </div>
    </div> -->
</div>

<Title>Current theme as JSON:</Title>
<JsonData data={theme} />

<!-- <style>

	.bg-primary-container {
		background-color: var(--md-sys-color-primary-container)
	}
	
	
	.bg-inverse-primary {
		background-color: var(--md-sys-color-inverse-primary)
	}
	
	
	.fill-inverse-primary {
		fill: var(--md-sys-color-inverse-primary)
	}
	
	</style> -->
<!-- 
<style>

	/* .badge-inverse-primary {
		background-color: var(--md-sys-color-inverse-primary);
		color: var(--md-sys-color-on-primary);
	}

	.btn-inverse-primary {
		--btn-color: var(--ip);
	} */

</style> -->