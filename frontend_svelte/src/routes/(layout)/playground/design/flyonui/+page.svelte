<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	// import { createRawSnippet, type Snippet } from 'svelte';

	import ColorTileFlyonUi from './ColorTileFlyonUI.svelte';
	import { type AppTheme } from '$lib/theming';
	import { themeStore } from '$lib/stores';
	// import { hexFromArgb } from '@material/material-color-utilities';
	import { onDestroy } from 'svelte';
	import JsonData from '$components/JsonData.svelte';
	import { initAccordion } from '$lib/userInterface';
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
	// 		name: 'primary-fixed-dim',
	// 		value: primaryFixedDimHex
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

	// for edit button:
	let edit = $state(false);
</script>

<div class="w-full xl:grid xl:grid-cols-2 xl:gap-4">
	<div class="col-span-2">
		<Heading>Colors</Heading>
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
			class="accordion accordion-bordered border-outline/40 divide-y {showSections.colors
				? ''
				: 'hidden'}"
			data-accordion-always-open=""
			{@attach initAccordion}
		>
			<!-- <div class="accordion-item accordion-item-active:scale-[1.05] accordion-item-active:mb-3 ease-in duration-300 delay-[1ms] active" id="default-colors"> -->
			<div class="active accordion-item border-outline/40" id="default-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="default-foreground-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
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
							<ColorTileFlyonUi>
								<div class="bg-primary {colorTileClasses}">
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
			<div class="active accordion-item border-outline/40" id="extension-materialui-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="extension-materialui-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">
						Extensions for foreground to FlyonUI with extra Material Design colors
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
			<div class="active accordion-item border-outline/40" id="default-background-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="default-background-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">Default background colors FlyonUI</p>
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
			<div class="active accordion-item border-outline/40" id="extension-materialui-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="extension-background-materialui-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
					></span>
					<p class="ml-10 text-base md:text-xl">
						Extensions for background to FlyonUI with extra Material Design colors
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
							<div class="bg-base-150 {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">base-150</p>
							</div>
						</ColorTileFlyonUi>
						<ColorTileFlyonUi>
							<div class="bg-base-250 {colorTileClasses}">
								<p class="text-surface-content {colorLabelClasses}">base-250</p>
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
							<div class="bg-base-content-variant {colorTileClasses}">
								<p class="text-inverse-surface-content {colorLabelClasses}">base-content-variant</p>
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
					</div>
				</div>
			</div>
			<div class="active accordion-item border-outline/40" id="opacity-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="opacity-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
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
						<div class="skeleton bg-primary flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl"></p>
						</div>
						<div class="skeleton bg-primary/10 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/10</p>
						</div>
						<div class="skeleton bg-primary/20 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/20</p>
						</div>
						<div class="skeleton bg-primary/30 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/30</p>
						</div>
						<div class="skeleton bg-primary/40 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/40</p>
						</div>
						<div class="skeleton bg-primary/50 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/50</p>
						</div>
						<div class="skeleton bg-primary/60 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/60</p>
						</div>
						<div class="skeleton bg-primary/70 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/70</p>
						</div>
						<div class="skeleton bg-primary/80 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/80</p>
						</div>
						<div class="skeleton bg-primary/90 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/90</p>
						</div>
						<div class="skeleton bg-primary/100 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/100</p>
						</div>
					</div>
					<p class="ml-5">Primary content:</p>
					<div class="m-5 grid grid-cols-4 gap-4 md:grid-cols-11">
						<div class="skeleton bg-primary-content flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl"></p>
						</div>
						<div class="skeleton bg-primary-content/10 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/10</p>
						</div>
						<div class="skeleton bg-primary-content/20 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/20</p>
						</div>
						<div class="skeleton bg-primary-content/30 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/30</p>
						</div>
						<div class="skeleton bg-primary-content/40 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/40</p>
						</div>
						<div class="skeleton bg-primary-content/50 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/50</p>
						</div>
						<div class="skeleton bg-primary-content/60 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/60</p>
						</div>
						<div class="skeleton bg-primary-content/70 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/70</p>
						</div>
						<div class="skeleton bg-primary-content/80 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/80</p>
						</div>
						<div class="skeleton bg-primary-content/90 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/90</p>
						</div>
						<div class="skeleton bg-primary-content/100 flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl">/100</p>
						</div>
					</div>
					<p class="ml-5">Primary container - this is an extension from material UI to flyonUI:</p>
					<div class="m-5 grid grid-cols-4 gap-4 md:grid-cols-11">
						<div class="skeleton bg-primary-container flex h-12 w-12 items-center justify-center">
							<p class="text-center text-xl"></p>
						</div>
						<div
							class="skeleton bg-primary-container/10 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/10</p>
						</div>
						<div
							class="skeleton bg-primary-container/20 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/20</p>
						</div>
						<div
							class="skeleton bg-primary-container/30 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/30</p>
						</div>
						<div
							class="skeleton bg-primary-container/40 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/40</p>
						</div>
						<div
							class="skeleton bg-primary-container/50 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/50</p>
						</div>
						<div
							class="skeleton bg-primary-container/60 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/60</p>
						</div>
						<div
							class="skeleton bg-primary-container/70 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/70</p>
						</div>
						<div
							class="skeleton bg-primary-container/80 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/80</p>
						</div>
						<div
							class="skeleton bg-primary-container/90 flex h-12 w-12 items-center justify-center"
						>
							<p class="text-center text-xl">/90</p>
						</div>
						<div
							class="skeleton bg-primary-container/100 flex h-12 w-12 items-center justify-center"
						>
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
			<div class="active accordion-item border-outline/40" id="avoid-colors">
				<button
					class="accordion-toggle inline-flex items-center gap-x-4 text-start"
					aria-controls="avoid-colors-collapse"
					aria-expanded="true"
				>
					<span
						class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180"
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
					</div>
				</div>
			</div>
			<div>
				<p class="text-xl italic">
					Note, for programmatically applied classes, add the utility class either programmatically
					via <code>Theming.addStyle( styleName, styles)</code>
					or as (scoped) <code>&ltstyle&gt</code> tag.
				</p>
			</div>
		</div>
	</div>

	<div class="col-span-2">
		<Heading>Utility classes</Heading>
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
				<li>primary-fixed-dim with primary-fixed-content (avoid using),</li>
				<li>error (also native in both - showing it works)</li>
				<li>error/50 (checking transparency from Tailwind)</li>
			</ul>
		</div>
		<div class="mt-5 grid grid-cols-5 gap-4 {showSections.utilityClasses ? '' : 'hidden'}">
			<div class="col-span-5 ml-5 text-2xl font-semibold">bg-"COLOR-NAME"</div>
			<div class="bg-primary text-primary-content h-24 p-4">bg-primary</div>
			<div class="bg-inverse-primary h-24 p-4">bg-inverse-primary</div>
			<div class="bg-primary-fixed-dim text-primary-content h-24 p-4">bg-primary-fixed-dim</div>
			<div class="bg-error text-error-content h-24 p-4">bg-error</div>
			<div class="bg-error/50 h-24 p-4">bg-error/50</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">
				from-"COLOR-NAME" via-"COLOR-NAME" to-"COLOR-NAME"
			</div>
			<div class="from-primary via-secondary to-accent h-24 bg-linear-to-r">
				from-primary via-scondary to-accent
			</div>
			<div class="from-success via-warning to-error h-24 bg-linear-to-r">
				from-success via-warning to-error
			</div>
			<div
				class="from-success via-warning to-error h-24 w-fit bg-linear-to-r bg-clip-text text-xl font-black text-transparent"
			>
				from-success via-warning to-error applied to text
			</div>
			<div class="from-primary via-inverse-primary to-primary-fixed-dim h-24 bg-linear-to-r">
				from-primary via-inverse-primary to-primary-fixed-dim
			</div>
			<div class="from-primary/50 via-secondary/50 to-accent/50 h-24 bg-linear-to-r">
				from-primary/50 via-scondary/50 to-accent/50
			</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">text-"COLOR-NAME"</div>
			<div class="text-primary h-24 text-xl font-bold md:text-3xl">text-primary</div>
			<div class="text-inverse-primary h-24 text-xl font-bold md:text-3xl">
				text-inverse-primary
			</div>
			<div class="text-primary-fixed-dim h-24 text-xl font-bold md:text-3xl">
				text-primary-fixed-dim
			</div>
			<div class="text-error h-24 text-xl font-bold md:text-3xl">text-error</div>
			<div class="text-error/50 h-24 text-xl font-bold md:text-3xl">text-error/50</div>

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
					name="radioPrimaryFixedDim"
					class="radio-primary-fixed-dim radio"
					id="radioPrimaryFixedDim"
					checked
				/>Radio primary fixed dim
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
			<button class="button ring-primary ring-3">ring-primary</button>
			<button class="button ring-inverse-primary ring-3">ring-inverse-primary</button>
			<button class="button ring-primary-fixed-dim ring-3">ring-primary-fixed-dim</button>
			<button class="button ring-error ring-3">ring-error</button>
			<button class="button ring-error/50 ring-3">ring-error/50</button>

			<div class="col-span-5 ml-5 text-2xl font-semibold">fill-"COLOR-NAME"</div>
			<svg class="fill-primary h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"
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
			<svg
				class="fill-primary-fixed-dim h-14"
				viewBox="0 0 46 48"
				xmlns="http://www.w3.org/2000/svg"
				><path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"
				></path></svg
			>
			<svg class="fill-error h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"
				><path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"
				></path></svg
			>
			<svg class="fill-error/50 h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"
				><path
					fill-rule="evenodd"
					clip-rule="evenodd"
					d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"
				></path></svg
			>

			<div class="col-span-5 ml-5 text-2xl font-semibold">caret-"COLOR-NAME"</div>
			<textarea class="caret-primary h-24">caret-primary: cursor color!</textarea>
			<textarea class="caret-inverse-primary h-24">caret-inverse-primary: cursor color!</textarea>
			<textarea class="caret-primary-fixed-dim h-24"
				>caret-primary-fixed-dim: cursor color!</textarea
			>
			<textarea class="caret-error h-24">caret-error: cursor color!</textarea>
			<textarea class="caret-error/50 h-24">caret-error/50: cursor color!</textarea>

			<div class="col-span-5 ml-5 text-2xl font-semibold">stroke-"COLOR-NAME"</div>
			<svg
				class="stroke-primary h-10"
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
				class="stroke-primary-fixed-dim h-10"
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
				class="stroke-error h-10"
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
				class="stroke-error/50 h-10"
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
			<div class="border-primary h-24 border-4">border-primary</div>
			<div class="border-inverse-primary h-24 border-4">border-inverse-primary</div>
			<div class="border-primary-fixed-dim h-24 border-4">border-primary-fixed-dim</div>
			<div class="border-error h-24 border-4">border-error</div>
			<div class="border-error/50 h-24 border-4">border-error/50</div>

			<div class="col-span-5 ml-5 text-2xl font-semibold">divide-"COLOR-NAME"</div>
			<div class="divide-primary h-24 divide-y-4">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>
			<div class="divide-inverse-primary h-24 divide-y-4">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>
			<div class="divide-primary-fixed-dim h-24 divide-y-4">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>
			<div class="divide-error h-24 divide-y-4">
				<div>divide</div>
				<div>between</div>
				<div>elements</div>
			</div>
			<div class="divide-error/50 h-24 divide-y-4">
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
				<input type="checkbox" class="accent-primary-fixed-dim" checked /> primary fixed dim
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
				<input type="checkbox" class="checkbox-primary-fixed-dim checkbox" checked /> primary fixed dim
			</label>
			<label>
				<input type="checkbox" class="checkbox checkbox-error" checked /> error
			</label>
			<label>
				<input type="checkbox" class="checkbox-error/50 checkbox" checked /> error/50
			</label>

			<div class="col-span-5 ml-5 text-2xl font-semibold">shadow-"COLOR-NAME"</div>
			<button class="btn btn-primary shadow-primary shadow-lg">Shadow primary</button>
			<button class="btn-inverse-primary btn shadow-inverse-primary shadow-lg"
				>Shadow inverse primary</button
			>
			<button class="btn-primary-fixed-dim btn shadow-primary-fixed-dim shadow-lg"
				>Shadow primary fixed dim</button
			>
			<button class="btn btn-error shadow-error shadow-lg">Shadow error</button>
			<button class="btn-error/50 btn shadow-error/50 shadow-lg">Shadow error/50</button>

			<div class="col-span-5 ml-5 text-2xl font-semibold">outline-"COLOR-NAME"</div>
			<button class="btn btn-primary btn-outline">primary</button>
			<button class="btn-inverse-primary btn btn-outline">inverse primary</button>
			<button class="btn-primary-fixed-dim btn btn-outline">primary fixed dim</button>
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
					class="switch-primary-fixed-dim switch switch-outline"
					id="switchPrimaryFixedDim"
					checked
				/>
				<label class="label label-text text-base" for="switchPrimaryFixedDim">
					Primary fixed dim
				</label>
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
			<div class="decoration-primary h-24 underline">decoration-primary</div>
			<div class="decoration-inverse-primary h-24 underline">decoration-inverse-primary</div>
			<div class="decoration-primary-fixed-dim h-24 underline">decoration-primary-fixed-dim</div>
			<div class="decoration-error h-24 underline">decoration-error</div>
			<div class="decoration-error/50 h-24 underline">decoration-error/50</div>

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
					class="input placeholder:text-inverse-primary"
					placeholder="Placeholder inverse primary"
					type="text"
					name="search"
				/>
			</label>
			<label class="relative block">
				<input
					class="input placeholder:text-primary-fixed-dim"
					placeholder="Placeholder primary fixed dim"
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
				class="badge ring-offset-primary col-span-5 ring-2 ring-red-300 ring-offset-4 md:col-span-1"
				>primary</span
			>
			<span
				class="badge ring-offset-inverse-primary col-span-5 ring-2 ring-red-300 ring-offset-4 md:col-span-1"
				>inverse primary</span
			>
			<span
				class="badge ring-offset-primary-fixed-dim col-span-5 ring-2 ring-red-300 ring-offset-4 md:col-span-1"
				>primary fixed dim</span
			>
			<span
				class="badge ring-offset-error col-span-5 ring-2 ring-blue-300 ring-offset-4 md:col-span-1"
				>error</span
			>
			<span
				class="badge ring-offset-error/50 col-span-5 ring-2 ring-blue-300 ring-offset-4 md:col-span-1"
				>error/50</span
			>
		</div>
	</div>

	<div>
		<Heading>Components with utility classes</Heading>
		<p>Badges:</p>
		<span class="badge badge-primary">Badge primary</span>
		<span class="badge badge-secondary">Badge secondary</span>
		<span class="badge badge-accent">Badge accent</span>
		<span class="badge-inverse-primary badge">Badge inverse primary</span>
		<span class="badge-primary-container badge">Badge primary container</span>
		<br />
		<p>Glass effect on button:</p>
		<button class="btn btn-primary glass">Glass on primary</button>
		<button class="btn-inverse-primary btn glass">Glass on inverse primary</button>
		<button class="btn-primary-fixed-dim btn glass">Glass on primary fixed dim</button>
		<button class="btn btn-error glass">Glass on error</button>
		<button class="btn-error/50 btn glass">Glass on error/50</button>
		<p>Using postCSS created components:</p>
		<span class="badge-primary-container badge">Badge primary-container</span>
		<span class="badge-my-personal badge">Badge my personal badge</span>
		<label>
			<input type="checkbox" class="checkbox-inverse-primary checkbox" checked /> inverse primary
		</label>
		<p>Buttons - default</p>
		<button class="btn btn-primary">primary</button>
		<button class="btn-inverse-primary btn">inverse primary</button>
		<button class="btn-primary-fixed-dim btn">primary fixed dim</button>
		<button class="btn btn-error">error</button>
		<button class="btn btn-error-container">error-container</button>
		<button class="btn-error/50 btn">error/50</button>
		<p>Buttons - soft</p>
		<button class="btn btn-primary btn-soft">soft primary</button>
		<button class="btn-inverse-primary btn btn-soft">soft inverse primary</button>
		<button class="btn-primary-fixed-dim btn btn-soft">soft primary fixed dim</button>
		<button class="btn btn-error btn-soft">soft error</button>
		<button class="btn btn-error-container btn-soft">soft error-container</button>
		<button class="btn-error/50 btn btn-soft">soft error/50</button>
		<p>Buttons - outline</p>
		<button class="btn btn-primary btn-outline">outline primary</button>
		<button class="btn-inverse-primary btn btn-outline">outline inverse primary</button>
		<button class="btn-primary-fixed-dim btn btn-outline">outline primary fixed dim</button>
		<button class="btn btn-error btn-outline">outline error</button>
		<button class="btn btn-error-container btn-outline">outline error-container</button>
		<button class="btn-error/50 btn btn-outline">outline error/50</button>
		<p>Buttons - text</p>
		<button class="btn btn-primary btn-text">text primary</button>
		<button class="btn-inverse-primary btn btn-text">text inverse primary</button>
		<button class="btn-primary-fixed-dim btn btn-text">text primary fixed dim</button>
		<button class="btn btn-error btn-text">text error</button>
		<button class="btn-error/50 btn btn-text">text error/50</button>
		<p>Buttons - gradient</p>
		<button class="btn btn-primary btn-gradient">gradient primary</button>
		<button class="btn-inverse-primary btn btn-gradient">gradient inverse primary</button>
		<button class="btn-primary-fixed-dim btn btn-gradient">gradient primary fixed dim</button>
		<button class="btn btn-error btn-gradient">gradient error</button>
		<button class="btn-error/50 btn btn-gradient">gradient error/50</button>
		<p>Buttons - rounded-full</p>
		<button class="btn btn-primary rounded-full">rounded-full primary</button>
		<button class="btn-inverse-primary btn rounded-full">rounded-full inverse primary</button>
		<button class="btn-primary-fixed-dim btn rounded-full">rounded-full primary fixed dim</button>
		<button class="btn btn-error rounded-full">rounded-full error</button>
		<button class="btn-error/50 btn rounded-full">rounded-full error/50</button>
		<p>Inputs:</p>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="input-filled w-full grow">
				<input type="text" placeholder="Primary colored input" class="input" id="filledInput" />
				<label class="input-filled-label" for="filledInput">Full name</label>
			</div>
			<div class="input-filled input-secondary w-full grow">
				<input
					type="text"
					placeholder="Secondary colored input"
					class="input border-secondary"
					id="filledInputSecondary"
				/>
				<label class="input-filled-label text-secondary" for="filledInputSecondary">Full name</label
				>
			</div>
			<div class="input-filled input-accent w-full grow">
				<input
					type="text"
					placeholder="Accent colored input"
					class="input"
					id="filledInputAccent"
				/>
				<label class="input-filled-label" for="filledInputAccent">Full name</label>
			</div>
			<div class="input-filled input-neutral w-full grow">
				<input
					type="text"
					placeholder="Neutral colored input"
					class="input"
					id="filledInputNeutral"
				/>
				<label class="input-filled-label" for="filledInputNeutral">Full name</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="input-filled w-full grow">
				<input type="text" placeholder="John Doe" class="input" id="filledInputDisabled" disabled />
				<label class="input-filled-label" for="filledInputDisabled">Full name - disabled</label>
			</div>
			<div class="input-filled w-full grow">
				<input type="text" placeholder="John Doe" class="input is-valid" id="filledInputIsValid" />
				<label class="input-filled-label" for="filledInputIsValid">Full name - is-valid</label>
			</div>
			<div class="input-filled w-full grow">
				<input
					type="text"
					placeholder="John Doe"
					class="input is-invalid"
					id="filledInputIsInvalid"
				/>
				<label class="input-filled-label" for="filledInputIsInvalid">Full name - is-invalid</label>
			</div>
			<div class="input-floating w-full grow">
				<input type="text" placeholder="John Doe" class="input" id="floatingInput" />
				<label class="input-floating-label" for="floatingInput">Full name - floating</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-xs" id="filledInputXs" />
				<label class="input-filled-label" for="filledInputXs">Full name - xs</label>
			</div>
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-sm" id="filledInputSm" />
				<label class="input-filled-label" for="filledInputSm">Full name - sm</label>
			</div>
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-md" id="filledInputDefault" />
				<label class="input-filled-label" for="filledInputDefault">Full name - default</label>
			</div>
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-lg" id="filledInputLg" />
				<label class="input-filled-label" for="filledInputLg">Full name - lg</label>
			</div>
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-xl" id="filledInputXl" />
				<label class="input-filled-label" for="filledInputXl">Full name - xl</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="input-filled input-error w-full grow">
				<input
					type="text"
					placeholder="John Doe"
					class="input input-xs sm:input-sm md:input-md lg:input-lg xl:input-xl"
					id="filledInputResponsive"
				/>
				<label class="input-filled-label" for="filledInputResponsive"
					>Full name - responsiveness not working!!</label
				>
			</div>
			<div class="input-floating w-full grow">
				<input
					type="text"
					placeholder="John Doe"
					class="input input-xs sm:input-sm md:input-md lg:input-lg xl:input-xl"
					id="filledInputResponsive"
				/>
				<label class="input-floating-label" for="filledInputResponsive"
					>Full name - responsive</label
				>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="textarea-filled w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledPrimary"></textarea>
				<label class="textarea-filled-label" for="textareaFilledPrimary">Your bio</label>
			</div>
			<div class="textarea-filled textarea-secondary w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledSecondary"></textarea>
				<label class="textarea-filled-label" for="textareaFlilledSecondary">Your bio</label>
			</div>
			<div class="textarea-filled textarea-accent w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledAccent"></textarea>
				<label class="textarea-filled-label" for="textareaFilledAccent">Your bio</label>
			</div>
			<div class="textarea-filled textarea-neutral w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledNeutral"></textarea>
				<label class="textarea-filled-label" for="textareaFilledNeutral">Your bio</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="textarea-filled w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledDisabled" disabled
				></textarea>
				<label class="textarea-filled-label" for="textareaFilledDisabled">Your bio</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea is-valid" placeholder="Hello!!!" id="textareaFilledIsValid"
				></textarea>
				<label class="textarea-filled-label" for="textareaFilledIsValid">Your bio</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea is-invalid" placeholder="Hello!!!" id="textareaFilledIsInvalid"
				></textarea>
				<label class="textarea-filled-label" for="textareaFilledIsInvalid">Your bio</label>
			</div>
			<div class="textarea-floating w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFloating"></textarea>
				<label class="textarea-floating-label" for="textareaFloating">Your bio</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-xs" placeholder="Hello!!!" id="filledTextareaXs"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareaXs">Your bio - xs</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-sm" placeholder="Hello!!!" id="filledTextareaSm"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareatSm">Your bio - sm</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-md" placeholder="Hello!!!" id="filledTextareaMd"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareaDefault">Your bio - default</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-lg" placeholder="Hello!!!" id="filledTextareaLg"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareaLg">Your bio - lg</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-xl" placeholder="Hello!!!" id="filledTextareaXl"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareaXl">Your bio - xl</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="textarea-filled w-full grow">
				<textarea
					class="textarea textarea-xs sm:textarea-sm md:textarea-md lg:textarea-lg xl:textarea-xl"
					placeholder="Hello!!!"
					id="filledTextareaResponsive"
				></textarea>
				<label class="textarea-filled-label" for="filleTextareaResponsive"
					>Your bio - responsive</label
				>
			</div>
			<div class="textarea-floating w-full grow">
				<textarea
					class="textarea textarea-xs sm:textarea-sm md:textarea-md lg:textarea-lg xl:textarea-xl"
					placeholder="Hello!!!"
					id="filledInputResponsive"
				></textarea>
				<label class="textarea-floating-label" for="filledTextareaResponsive"
					>Your bio - responsive</label
				>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="select-filled w-full grow">
				<select class="select" aria-label="Select filled" id="filledSelect">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelect">Pick your favorite Movie</label>
			</div>
			<div class="select-filled select-secondary w-full grow">
				<select class="select" aria-label="Select filled" id="filledSelectSecondary">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectSecondary"
					>Pick your favorite Movie</label
				>
			</div>
			<div class="select-filled select-accent w-full grow">
				<select class="select" aria-label="Select filled" id="filledSelectAccent">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectAccent">Pick your favorite Movie</label>
			</div>
			<div class="select-filled select-neutral w-full grow">
				<select class="select" aria-label="Select filled" id="filledSelectNeutral">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectNeutral">Pick your favorite Movie</label
				>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="select-filled w-full grow">
				<select class="select" aria-label="Select filled" id="filledSelectDisabled" disabled>
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectDisabled"
					>Pick your favorite Movie</label
				>
			</div>
			<div class="select-filled w-full grow">
				<select class="select is-valid" aria-label="Select filled" id="filledSelectIsvalid">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectIsvalid">Pick your favorite Movie</label
				>
			</div>
			<div class="select-filled w-full grow">
				<select class="select is-invalid" aria-label="Select filled" id="filledSelectIsinvalid">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectIsinvalid"
					>Pick your favorite Movie</label
				>
			</div>
			<div class="select-floating w-full grow">
				<select class="select" aria-label="Select floating label" id="floatingSelect">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-floating-label" for="floatingSelect">Pick your favorite Movie</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="select-filled w-full grow">
				<select class="select select-xs" aria-label="Select filled" id="filledSelectXs">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectXs">Pick your favorite Movie</label>
			</div>
			<div class="select-filled w-full grow">
				<select class="select select-sm" aria-label="Select filled" id="filledSelectSm">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectSm">Pick your favorite Movie</label>
			</div>
			<div class="select-filled w-full grow">
				<select class="select select-md" aria-label="Select filled" id="filledSelectMd">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectMd">Pick your favorite Movie</label>
			</div>
			<div class="select-filled w-full grow">
				<select class="select select-lg" aria-label="Select filled" id="filledSelectLg">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectLg">Pick your favorite Movie</label>
			</div>
			<div class="select-filled w-full grow">
				<select class="select select-xl" aria-label="Select filled" id="filledSelectXl">
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectXl">Pick your favorite Movie</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="select-filled w-full grow">
				<select
					class="select select-xs sm:select:sm md:select-md lg:select-lg xl:select-xl"
					aria-label="Select filled"
					id="filledSelectResponsive"
				>
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-filled-label" for="filledSelectResponsive"
					>Pick your favorite Movie</label
				>
			</div>
			<div class="select-floating w-full grow">
				<select
					class="select select-xs sm:select:sm md:select-md lg:select-lg xl:select-xl"
					aria-label="Select floating"
					id="floatingSelectResponsive"
				>
					<option>The Godfather</option>
					<option>The Shawshank Redemption</option>
					<option>Pulp Fiction</option>
					<option>The Dark Knight</option>
					<option>Schindler's List</option>
				</select>
				<label class="select-floating-label" for="floatingSelectResponsive"
					>Pick your favorite Movie</label
				>
			</div>
		</div>
	</div>

	<div>
		<Heading>Typography</Heading>
		<link rel="preconnect" href="https://fonts.googleapis.com" />
		<p class="text-center">Fonts families</p>
		<div class="grid grid-cols-1 divide-y-4">
			<div class="py-2 font-sans">
				Use class <em>font-sans</em> as font family, should be using <b>Robot</b> Google Fonts
				extending default theme in <code>app.css</code>.
			</div>
			<div class="py-2 font-serif">
				Use class <em>font-serif</em> as font family, should be using <b>Merriweather</b> Google
				Fonts, extending default theme in <code>app.css</code>.
			</div>
			<div class="py-2 font-mono">
				Use class <em>font-mono</em> as font family, still <b>TailwindCSS</b> default, not
				overwritten in
				<code>app.css</code> yet
			</div>
		</div>
		<p class="pt-5 text-center">Typography styles for Display</p>
		<div class="grid grid-cols-1 divide-y-4">
			<p class="display-large py-4">
				Some long eyecatcher in <i>Display - large</i> typography.
			</p>
			<p class="display py-4">Another eyecatcher in <i>Display</i> typography.</p>
			<p class="display-small py-4">
				And a third eyecatcher in <i>Display - small</i> typography.
			</p>
		</div>
		<p class="pt-5 text-center">Typography styles for Heading</p>
		<div class="grid grid-cols-1 divide-y-4">
			<p class="heading-large py-4">
				A <i>Heading - large</i> typography with long enough text to get a line break.
			</p>
			<p class="heading py-4">
				Another <i>Heading</i> typography with long enough text to get a line break.
			</p>
			<p class="heading-small py-4">
				And a third <i>Heading - small</i> typography with long enough text to get a line break.
			</p>
		</div>
		<p class="pt-5 text-center">Typography styles for Title</p>
		<div class="grid grid-cols-1 divide-y-4">
			<p class="title-large py-4">
				This is a <i>Title - large</i> typography with some extended text to be long enough to create
				a line break.
			</p>
			<p class="title py-4">
				And that is another <i>Title</i> typography with some text to fill the line, so we can get a
				line break, which requires long enough text get the line breaking over into a new line.
			</p>
			<p class="title-small py-4">
				And the third <i>Title - small</i> typography needs quite some extra meaningless text, just to
				demonstrate the line break even on larger screens, where it might get hard to provoke a line
				break with such small text, but we'll get there with to make the text long enough text to get
				a line break.
			</p>
		</div>
		<p class="pt-5 text-center">Typography styles for Body</p>
		<div class="grid grid-cols-1 divide-y-4">
			<p class="body-large py-4">
				This is a longer text in <i>Body - large</i> typography with long enough text to get more than
				a line break. Note that the font changed to a serif font, which should make it easier to read
				for longer text on a screen.
			</p>
			<p class="body py-4">
				And that is another <i>Body</i> typography with even more text to fill the line, so we can get
				a line break, which requires long enough text get the line breaking over into a new line.
			</p>
			<p class="body-small py-4">
				And a third <i>Body - small</i> typography which needs even more meaningless text to make sure,
				the line is eventually breaking, even on larger screens, where it might get hard to provoke a
				line break with such small text, but we'll get there with to make the text long enough text to
				get a line break.
			</p>
		</div>
		<p class="pt-5 text-center">Typography styles for Labels - demonstrated in a badge</p>
		<div class="grid grid-cols-2 gap-4">
			<div class="label-large badge badge-xl rounded-full">Label large</div>
			<div class="label-large label-prominent badge badge-xl rounded-full">
				Label large prominent
			</div>
			<span class="label badge badge-lg rounded-full">Label</span>
			<span class="label-prominent label badge badge-lg rounded-full">Label prominent</span>
			<span class="label-small badge rounded-full px-4">Label small</span>
			<span class="label-small label-prominent badge rounded-full px-4">Label small prominent</span>
		</div>
	</div>

	<div>
		<Heading>Styles</Heading>
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
		<Heading>Icons</Heading>
		<p class="title-large text-center text-xl">Iconify with FlyonUI</p>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div>
				<p class="label text-center">
					Default library <span class="label-prominent badge min-h-fit">Tablers</span>
				</p>
				<span class="icon-[tabler--settings] size-12"></span>
				<span class="icon-[tabler--palette] size-12"></span>
				<span class="icon-[tabler--home] size-12"></span>
				<span class="icon-[tabler--user] size-12"></span>
				<span class="icon-[tabler--trash] size-12"></span>
				<span class="icon-[tabler--send-2] size-12"></span>
				<span class="icon-[tabler--share-2] size-12"></span>
				<span class="icon-[tabler--ban] size-12"></span>
				<span class="icon-[tabler--info-triangle] size-12"></span>
				<span class="icon-[tabler--link-off] size-12"></span>
				<span class="icon-[tabler--link] size-12"></span>
				<span class="icon-[tabler--ai] size-12"></span>
				<span class="icon-[tabler--eye] size-12"></span>
				<span class="icon-[tabler--apps] size-12"></span>
				<span class="icon-[tabler--arrow-iteration] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Material Symbols</span>
				</p>
				<span class="icon-[material-symbols--settings-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--palette-outline] size-12"></span>
				<span class="icon-[material-symbols--home-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--person-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--edit-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--folder-outline-rounded] size-12"></span>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit"
						>Google Material Icons</span
					>
				</p>
				<span class="icon-[ic--round-question-mark] size-12"></span>
				<span class="icon-[ic--outline-share] size-12"></span>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit"
						>Material Design Icons</span
					>
				</p>
				<span class="icon-[mdi--feature-highlight] size-12"></span>
				<span class="icon-[mdi--text] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">SVG spinners</span>
				</p>
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
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Font Awesome Solid</span>
				</p>
				<span class="icon-[fa6-solid--user] size-12"></span>
				<span class="icon-[fa6-solid--user-group] size-12"></span>
				<span class="icon-[fa6-solid--droplet] size-12"></span>
				<span class="icon-[fa6-solid--comments] size-12"></span>
				<span class="icon-[fa6-solid--plus] size-12"></span>
				<span class="icon-[fa6-solid--chalkboard] size-12"></span>
				<span class="icon-[fa7-solid--link] size-12"></span>
				<span class="icon-[fa7-solid--unlink] size-12"></span>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Font Awesome</span>
				</p>
				<span class="icon-[fa--users] size-12"></span>
				<span class="icon-[fa--institution] size-12"></span>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Font Awesome Brands</span>
				</p>
				<span class="icon-[fa6-brands--discord] size-12"></span>
				<span class="icon-[fa6-brands--youtube] size-12"></span>
				<span class="icon-[fa6-brands--linux] size-12"></span>
				<span class="icon-[fa6-brands--github] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Feather Icon</span>
				</p>
				<span class="icon-[fe--bell] size-12"></span>
				<span class="icon-[fe--disabled] size-12"></span>
				<span class="grid place-items-center">
					<span class="icon-[fe--bell] col-start-1 row-start-1 size-8"></span>
					<span class="icon-[fe--disabled] col-start-1 row-start-1 size-12"></span>
				</span>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Phosphor</span>
				</p>
				<span class="icon-[ph--users-four-fill] size-12"></span>
				<span class="icon-[ph--smiley] size-12"></span>
				<span class="icon-[ph--smiley-duotone] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Fluent (Microsoft)</span>
				</p>
				<span class="icon-[fluent--people-team-16-filled] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Bootstrap Icons</span>
				</p>
				<span class="icon-[bi--microsoft-teams] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Mingcute</span>
				</p>
				<span class="icon-[mingcute--check-2-fill] size-12"></span>
				<span class="icon-[mingcute--ai-fill] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Emoji library <span class="label-prominent badge min-h-fit">Noto emoji</span>
				</p>
				<span class="icon-[noto--folded-hands] size-12"></span>
				<span class="icon-[noto--folded-hands-medium-dark-skin-tone] size-12"></span>
				<span class="icon-[noto--heart-hands] size-12"></span>
				<span class="icon-[noto--heart-hands-dark-skin-tone] size-12"></span>
				<span class="icon-[noto--fire] size-12"></span>
				<span class="icon-[noto--smiling-face-with-sunglasses] size-12"></span>
				<span class="icon-[noto--check-mark-button] size-12"></span>
				<span class="icon-[noto--cross-mark] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Emoji library <span class="label-prominent badge min-h-fit">Openmoji</span>
				</p>
				<span class="icon-[openmoji--check-mark] size-12"></span>
				<span class="icon-[openmoji--cross-mark] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Emoji library <span class="label-prominent badge min-h-fit">Twitter Emoji</span>
				</p>
				<span class="icon-[twemoji--flag-denmark] size-12"></span>
				<span class="icon-[twemoji--flag-germany] size-12"></span>
				<span class="icon-[twemoji--flag-united-states] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					<span class="label-prominent badge min-h-fit">Maki</span>
				</p>
				<span class="icon-[maki--construction] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					<span class="label-prominent badge min-h-fit">Streamline</span>
				</p>
				<span class="icon-[streamline--hierarchy-2] size-12"></span>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<div>
		<Heading>Buttons</Heading>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div>
				<p class="label text-center">Action Buttons</p>
				<button class="btn-neutral-container btn btn-circle btn-gradient" aria-label="Add">
					<span class="icon-[fa6-solid--plus]"></span>
				</button>
				<button class="btn-info-container btn btn-circle btn-gradient" aria-label="Edit">
					<span class="icon-[material-symbols--edit-outline-rounded]"></span>
				</button>
				<button class="btn-error-container btn btn-circle btn-gradient" aria-label="Delete">
					<span class="icon-[tabler--trash]"></span>
				</button>
				<button class="btn-secondary-container btn btn-circle btn-gradient" aria-label="Send">
					<span class="icon-[tabler--send-2]"></span>
				</button>
				<button class="btn-success-container btn btn-circle btn-gradient" aria-label="Share">
					<span class="icon-[tabler--share-2]"></span>
				</button>
				<button class="btn-success-container btn btn-circle btn-gradient" aria-label="Done">
					<span class="icon-[mingcute--check-2-fill]"></span>
				</button>
				<p class="label text-center">State changing buttons</p>
				<button
					class="btn-info-container btn btn-circle btn-gradient"
					onclick={() => (edit ? (edit = false) : (edit = true))}
					aria-label="Edit Button"
				>
					<span class="grid place-items-center">
						<span class="icon-[material-symbols--edit-outline-rounded] col-start-1 row-start-1"
						></span>
						<span class="icon-[fe--disabled] col-start-1 row-start-1 size-6 {edit ? '' : 'hidden'}"
						></span>
					</span>
				</button>
			</div>
		</div>
	</div>

	<div>
		<Heading>Badges</Heading>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div>
				<p class="label text-center">Text Badges</p>
			</div>
		</div>
	</div>

	<div>
		<Heading>Swaps</Heading>
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

	<!-- <div>
        <Heading>Menus</Heading>
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

<Heading>Current theme as JSON:</Heading>
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
