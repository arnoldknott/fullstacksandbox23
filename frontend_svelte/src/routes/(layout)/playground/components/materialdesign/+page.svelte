<script lang="ts">
	import ColorTileMaterialUi from '$components/ColorTileMaterialUI.svelte';
	import '@material/web/icon/icon.js';
	import '@material/web/list/list.js';
	import '@material/web/list/list-item.js';
	import '@material/web/dialog/dialog.js';
	import type { Dialog } from '@material/web/dialog/internal/dialog';
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	import '@material/web/button/filled-tonal-button.js';
	import '@material/web/select/filled-select.js';
	import '@material/web/select/select-option.js';
	import '@material/web/list/list.js';
	import '@material/web/list/list-item.js';
	import '@material/web/labs/card/elevated-card.js';
	import '@material/web/labs/card/filled-card.js';
	import '@material/web/labs/card/outlined-card.js';
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import JsonData from '$components/JsonData.svelte';
	// import { getContext } from 'svelte';
	import { themeStore } from '$lib/stores';
	import type { AppTheme } from '$lib/theming';
	// import { get } from 'svelte/store';
	// import { currentTheme } from '(layout)/layout.svelte';
	import { onDestroy } from 'svelte';
	import { Hct, hexFromArgb } from '@material/material-color-utilities';

	let showSections = $state({
		colors: true,
		palettes: true,
		typography: true,
		shapes: true,
		sliders: true
	});
	// let theme = $state(getContext('theme'));
	// let palettes = $themeStore.light.palettes;
	// console.log('palettes:', palettes);
	let theme = $state({} as AppTheme);
	const unsbscribeThemeStore = themeStore.subscribe((value) => {
		theme = value;
	});
	let palettes = $derived.by(() => {
		if (!theme.currentMode) {
			return '';
		} else {
			return theme[theme.currentMode].palettes;
		}
	});
	// $effect(() => {console.log('palettes:', palettes)})
	// let toneValues = $state({} as {key: string})
	// let toneValues = $derived(
	//     Object.fromEntries(
	//         Object.entries(palettes).map(([key, value]) => [key, value.keyColor.tone])
	//     )
	// );
	let palettesArray = $derived(
		palettes
			? Object.entries(palettes).map(([key, value]) => {
					// const currentTone = value.keyColor.tone;
					// toneValues[key] = value.keyColor.tone;
					// return { name: key, currentTone: currentTone, ...value };
					return { name: key, ...value };
				})
			: []
	);
	let toneValues = $state({} as Record<string, number>);
	$effect(() => {
		palettesArray.forEach((palette) => {
			const key = palette.name as keyof typeof toneValues;
			toneValues[key] = palette.keyColor.tone;
		});
	});
	// $effect(() => {console.log('palettes:', palettesArray)})
	// console.log('themeStore:', $themeStore);
	// console.log(getContext('theme'))
	// let theme = $state(getContext('theme'));
	// $effect(() => { console.log('theme:', theme)} );

	// for HCT:
	// red: hue = 25,
	// (yellow: hue = 104,)
	// green: hue = 130
	// use chroma and tone from error container - always keeps the color!
	// text on it:
	// chorma and tone always from "on error container"
	let errorContainerHct = $derived.by(() => {
		if (!theme.currentMode) {
			return Hct.from(25, 80, 30);
		} else {
			return Hct.fromInt(theme[theme.currentMode].colors['error']);
		}
	});
	let onErrorContainerHct = $derived.by(() => {
		if (!theme.currentMode) {
			return Hct.from(24, 13, 90);
		} else {
			return Hct.fromInt(theme[theme.currentMode].colors['onError']);
		}
	});
	// console.log('errorContainerHct:', errorContainerHct);
	let status = $state([50, 0, 100]);
	let statusColorsHue = $derived([
		{
			background: status[0] * 1.05 + 25,
			text: status[0] * 1.05 + 25
		},
		{
			background: status[1] * 1.05 + 25,
			text: status[0] * 1.05 + 25
		},
		{
			background: status[2] * 1.05 + 25,
			text: status[0] * 1.05 + 25
		}
	]);
	let statusColors = $derived([
		{
			background: hexFromArgb(
				Hct.from(
					statusColorsHue[0].background,
					errorContainerHct.chroma,
					errorContainerHct.tone
				).toInt()
			),
			text: hexFromArgb(
				Hct.from(
					statusColorsHue[0].text,
					onErrorContainerHct.chroma,
					onErrorContainerHct.tone
				).toInt()
			)
		},
		{
			background: hexFromArgb(
				Hct.from(
					statusColorsHue[1].background,
					errorContainerHct.chroma,
					errorContainerHct.tone
				).toInt()
			),
			text: hexFromArgb(
				Hct.from(
					statusColorsHue[1].text,
					onErrorContainerHct.chroma,
					onErrorContainerHct.tone
				).toInt()
			)
		},
		{
			background: hexFromArgb(
				Hct.from(
					statusColorsHue[2].background,
					errorContainerHct.chroma,
					errorContainerHct.tone
				).toInt()
			),
			text: hexFromArgb(
				Hct.from(
					statusColorsHue[2].text,
					onErrorContainerHct.chroma,
					onErrorContainerHct.tone
				).toInt()
			)
		}
	]);
	// let statusColors = $derived([
	// 	`hsl(${status[0] * 1.2}, 80%, 80%)`,
	// 	`hsl(${status[1] * 1.2}, 80%, 80%)`,
	// 	`hsl(${status[2] * 1.2}, 80%, 80%)`,
	// ]);

	let demoResourceDialog: Dialog;
	// let name = $state('');
	// let description = $state('');
	// let language = $state('en-US');
	const cancelForm = (event: Event) => {
		event.preventDefault();
		demoResourceDialog.close();
	};

	type Props = { type: 'login' | 'signup' };
	let { type }: Props = $props();
	const button = type === 'signup' ? 'Sign up' : 'Log in'; // untested!
	onDestroy(() => {
		unsbscribeThemeStore();
	});
</script>

<!-- <JsonData data={palettesArray} /> -->
<!-- <JsonData data={theme} /> -->

<div class="grid w-full grid-cols-1 gap-4 xl:grid-cols-2">
	<div class="xl:col-span-2">
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
		<div class={showSections.colors ? '' : 'hidden'}>
			<p class="text-center text-2xl">Dynamic colors Material Color Utilities</p>
			<div class="grid w-full grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-8">
				<p class="col-span-2 text-center text-xl md:col-span-4 xl:col-span-4">
					Default Foreground Material Design
				</p>
				<p class="hidden text-center text-xl xl:col-span-4 xl:block">
					Extended Foreground to match FlyonUI (8 columns)
				</p>
				<div>
					<ColorTileMaterialUi
						background="--md-sys-color-primary"
						color="--md-sys-color-on-primary"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-primary"
						color="--md-sys-color-primary"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-primary-container"
						color="--md-sys-color-on-primary-container"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-primary-container"
						color="--md-sys-color-primary-container"
					/>
				</div>
				<div>
					<ColorTileMaterialUi
						background="--md-sys-color-secondary"
						color="--md-sys-color-on-secondary"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-secondary"
						color="--md-sys-color-secondary"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-secondary-container"
						color="--md-sys-color-on-secondary-container"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-secondary-container"
						color="--md-sys-color-secondary-container"
					/>
				</div>
				<div>
					<ColorTileMaterialUi
						background="--md-sys-color-tertiary"
						color="--md-sys-color-on-tertiary"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-tertiary"
						color="--md-sys-color-tertiary"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-tertiary-container"
						color="--md-sys-color-on-tertiary-container"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-tertiary-container"
						color="--md-sys-color-tertiary-container"
					/>
				</div>
				<div>
					<ColorTileMaterialUi background="--md-sys-color-error" color="--md-sys-color-on-error" />
					<ColorTileMaterialUi background="--md-sys-color-on-error" color="--md-sys-color-error" />
					<ColorTileMaterialUi
						background="--md-sys-color-error-container"
						color="--md-sys-color-on-error-container"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-error-container"
						color="--md-sys-color-error-container"
					/>
				</div>
				<p class="col-span-2 text-center text-xl md:col-span-4 xl:col-span-4 xl:hidden">
					Extended Foreground to match FlyonUI
				</p>
				<div>
					<ColorTileMaterialUi
						background="--md-sys-color-warning"
						color="--md-sys-color-on-warning"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-warning"
						color="--md-sys-color-warning"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-warning-container"
						color="--md-sys-color-on-warning-container"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-warning-container"
						color="--md-sys-color-warning-container"
					/>
				</div>
				<div>
					<ColorTileMaterialUi
						background="--md-sys-color-success"
						color="--md-sys-color-on-success"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-success"
						color="--md-sys-color-success"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-success-container"
						color="--md-sys-color-on-success-container"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-success-container"
						color="--md-sys-color-success-container"
					/>
				</div>
				<div>
					<ColorTileMaterialUi background="--md-sys-color-info" color="--md-sys-color-on-info" />
					<ColorTileMaterialUi background="--md-sys-color-on-info" color="--md-sys-color-info" />
					<ColorTileMaterialUi
						background="--md-sys-color-info-container"
						color="--md-sys-color-on-info-container"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-info-container"
						color="--md-sys-color-info-container"
					/>
				</div>
				<div>
					<ColorTileMaterialUi
						background="--md-sys-color-neutral"
						color="--md-sys-color-on-neutral"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-neutral"
						color="--md-sys-color-neutral"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-neutral-container"
						color="--md-sys-color-on-neutral-container"
					/>
					<ColorTileMaterialUi
						background="--md-sys-color-on-neutral-container"
						color="--md-sys-color-neutral-container"
					/>
				</div>
			</div>
			<div class="mt-8 grid w-full grid-cols-2 gap-4 md:grid-cols-5">
				<p class="col-span-2 text-center text-xl md:col-span-5">
					Default Background Material Design
				</p>
				<ColorTileMaterialUi
					background="--md-sys-color-surface-container-lowest"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-surface-container-low"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-surface-container"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-surface-container-high"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-surface-container-highest"
					color="--md-sys-color-on-surface"
				/>
			</div>
			<div class="mt-8 grid w-full grid-cols-2 gap-4 md:grid-cols-4">
				<ColorTileMaterialUi
					background="--md-sys-color-on-surface"
					color="--md-sys-color-inverse-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-on-surface-variant"
					color="--md-sys-color-inverse-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-outline"
					color="--md-sys-color-inverse-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-outline-variant"
					color="--md-sys-color-inverse-on-surface"
				/>
			</div>
			<div class="mt-8 grid w-full grid-cols-2 gap-4 md:grid-cols-5">
				<ColorTileMaterialUi
					background="--md-sys-color-inverse-surface"
					color="--md-sys-color-inverse-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-inverse-on-surface"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-inverse-primary"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi background="--md-sys-color-scrim" color="--md-sys-color-on-surface" />
				<ColorTileMaterialUi background="--md-sys-color-shadow" color="--md-sys-color-on-surface" />
			</div>
			<div class="mt-8 grid w-full grid-cols-2 gap-4 md:grid-cols-4">
				<ColorTileMaterialUi
					background="--md-sys-color-background"
					color="--md-sys-color-on-background"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-on-background"
					color="--md-sys-color-background"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-neutral-palette-key-color"
					color="--md-sys-color-inverse-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-neutral-variant-palette-key-color"
					color="-md-sys-color-inverse-on-surface"
				/>
			</div>
			<div class="mt-8 grid w-full grid-cols-3 gap-4">
				<ColorTileMaterialUi
					background="--md-sys-color-primary-palette-key-color"
					color="--md-sys-color-on-background"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-secondary-palette-key-color"
					color="--md-sys-color-background"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-tertiary-palette-key-color"
					color="--md-sys-color-inverse-on-surface"
				/>
			</div>
			<div class="mt-8 grid w-full grid-cols-2 gap-4 md:grid-cols-4">
				<p class="col-span-2 text-center text-xl md:col-span-4">
					Avoid using those - the fixed colors don't switch from light to dark mode
				</p>
				<ColorTileMaterialUi
					background="--md-sys-color-primary-fixed"
					color="--md-sys-color-on-primary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-primary-fixed-dim"
					color="--md-sys-color-on-primary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-on-primary-fixed"
					color="--md-sys-color-primary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-on-primary-fixed-variant"
					color="--md-sys-color-primary-fixed"
				/>
			</div>
			<div class="mt-8 grid w-full grid-cols-2 gap-4 md:grid-cols-4">
				<ColorTileMaterialUi
					background="--md-sys-color-secondary-fixed"
					color="--md-sys-color-on-secondary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-secondary-fixed-dim"
					color="--md-sys-color-on-secondary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-on-secondary-fixed"
					color="--md-sys-color-secondary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-on-secondary-fixed-variant"
					color="--md-sys-color-secondary-fixed"
				/>
			</div>
			<div class="mt-8 grid w-full grid-cols-2 gap-4 md:grid-cols-4">
				<ColorTileMaterialUi
					background="--md-sys-color-tertiary-fixed"
					color="--md-sys-color-on-tertiary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-tertiary-fixed-dim"
					color="--md-sys-color-on-tertiary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-on-tertiary-fixed"
					color="--md-sys-color-tertiary-fixed"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-on-tertiary-fixed-variant"
					color="--md-sys-color-tertiary-fixed"
				/>
			</div>
			<div class="mt-8 grid w-full grid-cols-2 gap-4 md:grid-cols-5">
				<ColorTileMaterialUi
					background="--md-sys-color-surface-dim"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-surface"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-surface-bright"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-surface-variant"
					color="--md-sys-color-on-surface"
				/>
				<ColorTileMaterialUi
					background="--md-sys-color-surface-tint"
					color="--md-sys-color-inverse-on-surface"
				/>
			</div>
			<HorizontalRule />
		</div>
	</div>

	<div class="xl:col-span-2">
		<Title>Palettes</Title>
		<div class="flex items-center gap-1">
			<label class="label label-text text-base" for="switchColors">Hide</label>
			<input
				type="checkbox"
				class="switch switch-primary"
				bind:checked={showSections.palettes}
				id="switchColors"
			/>
			<label class="label label-text text-base" for="switchColors">Show</label>
		</div>
		<div class={showSections.palettes ? '' : 'hidden'}>
			{#each palettesArray as palette}
				<div class="mb-5 grid w-full grid-cols-1 gap-4 md:grid-cols-2">
					<div class="flex flex-col">
						<p class="text-center text-2xl">{palette.name}</p>
						<div class="grid grid-cols-2">
							<div
								class="flex h-24 grow p-2"
								style="background-color: {hexFromArgb(palette.keyColor.toInt())};"
							>
								<p class="text-center text-2xl">Key Color</p>
							</div>
							<div
								class="flex h-24 grow p-2"
								style="background-color: {hexFromArgb(
									Hct.from(
										palette.keyColor.hue,
										palette.keyColor.chroma,
										toneValues[palette.name]
									).toInt()
								)};"
							>
								<p class="text-center text-2xl">Current Tone</p>
							</div>
						</div>
						<div class="mt-5 flex flex-row">
							<p class="basis-1/12 text-xl">Tone:</p>
							<input
								class="range basis-10/12"
								type="range"
								min="0"
								max="100"
								bind:value={toneValues[palette.name]}
								aria-label="range"
							/>
							<p class="basis-1/12 text-right text-xl">
								{Math.round(toneValues[palette.name] * 100) / 100} %
								<md-filled-button
									onclick={() => (toneValues[palette.name] = palette.keyColor.tone)}
									role="button"
									tabindex="0"
									onkeydown={(event: KeyboardEvent) =>
										event.key === 'Enter'
											? (toneValues[palette.name] = palette.keyColor.tone)
											: null}
								>
									Reset
								</md-filled-button>
							</p>
						</div>
					</div>
					<div>
						<JsonData data={palette} />
					</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- <div class="staticMaterialThemeBuilder">
		<Title>Colors</Title>
		<p class="text-center text-2xl">
			(static generated on Material Theme Builder homepage and exported as css variables)
		</p>
		<div class="grid grid-cols-12 gap-4">
			<p class="col-span-12">Sys color primary:</p>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-primary);"
			>
				<p class="text-center text-xl">1</p>
			</div>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-surface-tint);"
			>
				<p class="text-center text-xl">2</p>
			</div>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-on-primary);"
			>
				<p class="text-center text-xl">3</p>
			</div>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-primary-container);"
			>
				<p class="text-center text-xl">4</p>
			</div>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-on-primary-container);"
			>
				<p class="text-center text-xl">5</p>
			</div>
		</div>
		<HorizontalRule />
	</div> -->

	<div>
		<Title>Typography</Title>
		<div class="flex items-center gap-1">
			<label class="label label-text text-base" for="switchTypography">Hide</label>
			<input
				type="checkbox"
				class="switch switch-primary"
				bind:checked={showSections.typography}
				id="switchTypography"
			/>
			<label class="label label-text text-base" for="switchTypography">Show</label>
		</div>
		<div class={showSections.typography ? '' : 'hidden'}>
			<p class="text-center text-2xl">Type face:</p>
			<ul>
				<li>
					Brand
					<ul>
						<li>--md-ref-typeface-brand</li>
					</ul>
				</li>
				<li>
					Plain
					<ul>
						<li>--md-ref-typeface-plain</li>
					</ul>
				</li>
			</ul>
			<p class="text-center text-2xl">Type scale:</p>
			<ul>
				<li>
					Display
					<ul>
						<li>--md-sys-typescale-display-medium-font</li>
						<li>--md-sys-typescale-display-medium-size</li>
						<li>--md-sys-typescale-display-medium-line-height</li>
						<li>--md-sys-typescale-display-medium-weight</li>
					</ul>
				</li>
				<li>
					Headline
					<ul>
						<li>--md-sys-typescale-headline-medium-font</li>
						<li>--md-sys-typescale-headline-medium-size</li>
						<li>--md-sys-typescale-headline-medium-line-height</li>
						<li>--md-sys-typescale-headline-medium-weight</li>
					</ul>
				</li>
				<li>
					Title
					<ul>
						<li>--md-sys-typescale-title-medium-font</li>
						<li>--md-sys-typescale-title-medium-size</li>
						<li>--md-sys-typescale-title-medium-line-height</li>
						<li>--md-sys-typescale-title-medium-weight</li>
					</ul>
				</li>
				<li>
					Body
					<ul>
						<li>--md-sys-typescale-body-medium-font</li>
						<li>--md-sys-typescale-body-medium-size</li>
						<li>--md-sys-typescale-body-medium-line-height</li>
						<li>--md-sys-typescale-body-medium-weight</li>
					</ul>
				</li>
				<li>
					Label
					<ul>
						<li>--md-sys-typescale-label-medium-font</li>
						<li>--md-sys-typescale-label-medium-size</li>
						<li>--md-sys-typescale-label-medium-line-height</li>
						<li>--md-sys-typescale-label-medium-weight</li>
					</ul>
				</li>
			</ul>
		</div>
	</div>

	<div>
		<Title>Shapes (styles)</Title>
		<div class="flex items-center gap-1">
			<label class="label label-text text-base" for="switchShapes">Hide</label>
			<input
				type="checkbox"
				class="switch switch-primary"
				bind:checked={showSections.shapes}
				id="switchShapes"
			/>
			<label class="label label-text text-base" for="switchshapes">Show</label>
		</div>
		<div class={showSections.shapes ? '' : 'hidden'}>
			<!-- <div class="text-left text-base md:text-xl bg-primary" style="border-radius: var(--md-sys-shape-corner-none);">
				corner-none
			</div>
			<div class="text-left text-base md:text-xl bg-primary" style="border-radius: var(--md-sys-shape-corner-full);">
				corner-full
			</div> -->
			<p class="text-center text-2xl">Supported tokens:</p>
			<ul>
				<li>--md-sys-shape-corner-none</li>
				<li>--md-sys-shape-corner-extra-small</li>
				<li>--md-sys-shape-corner-small</li>
				<li>--md-sys-shape-corner-medium</li>
				<li>--md-sys-shape-corner-large</li>
				<li>--md-sys-shape-corner-extra-large</li>
				<li>--md-sys-shape-corner-full</li>
			</ul>
			<p>The 7 values are not available - demonstrating the 9 steps of tailwindsCSS instead:</p>
			<div class="grid grid-cols-2 gap-4 p-4 md:grid-cols-5">
				{#each ['none', 'sm', '', 'md', 'lg', 'xl', '2xl', '3xl', 'full'] as style}
					<div
						class="m-2 w-24 bg-primary-container p-2 text-center text-base md:text-xl rounded-{style}"
					>
						{style}
					</div>
				{/each}
			</div>
		</div>
	</div>

	<div>
		<Title>Status sliders with HCT</Title>

		<div class="grid grid-cols-3 gap-4">
			<div class="w-full">
				<label class="label label-text" for="leftStatus"
					>Left Color: <span class="label">
						<code class="label-text-alt">{status[0]}</code>
					</span></label
				>
				<input
					type="range"
					min="0"
					max="100"
					step="1"
					class="range w-full"
					aria-label="left Status"
					id="leftStatus"
					bind:value={status[0]}
				/>
			</div>
			<div class="w-full">
				<label class="label label-text" for="leftStatus"
					>Center Color: <span class="label">
						<code class="label-text-alt">{status[1]}</code>
					</span></label
				>
				<input
					type="range"
					min="0"
					max="100"
					step="1"
					class="range w-full"
					aria-label="left Status"
					id="leftStatus"
					bind:value={status[1]}
				/>
			</div>
			<div class="w-full">
				<label class="label label-text" for="leftStatus"
					>Right Color: <span class="label">
						<code class="label-text-alt">{status[2]}</code>
					</span></label
				>
				<input
					type="range"
					min="0"
					max="100"
					step="1"
					class="range w-full"
					aria-label="left Status"
					id="leftStatus"
					bind:value={status[2]}
				/>
			</div>
		</div>
		<div class="grid grid-cols-3">
			<div
				class="flex h-20 w-full items-center justify-center text-2xl"
				style="background: linear-gradient(to right, {statusColors[0].background}, {statusColors[0]
					.background}, {statusColors[1].background});"
			>
				Left
			</div>
			<div
				class="flex h-20 w-full items-center justify-center text-2xl"
				style="background: linear-gradient(to right, {statusColors[1].background}, {statusColors[1]
					.background}, {statusColors[1].background});"
			>
				Center
			</div>
			<div
				class="flex h-20 w-full items-center justify-center text-2xl"
				style="background: linear-gradient(to right, {statusColors[1].background}, {statusColors[2]
					.background}, {statusColors[2].background});"
			>
				Right
			</div>
			<!-- <div
				class="flex h-20 w-full items-center justify-center text-2xl"
				style="background: linear-gradient(to right, {statusColors[1]}, {statusColors[2]});"
			></div> -->
		</div>
	</div>

	<div>
		<Title>Icons</Title>
		<p>Don't use - iconify has them as well and well integrated with FlyonUI</p>
		<div class="grid grid-cols-5 gap-4">
			<div>
				<p class="text-center text-2xl">Supported tokens:</p>
				<ul>
					<li>--md-icon-font: 'Material Symbols Rounded'</li>
					<li>--md-icon-size: 24px</li>
				</ul>
			</div>
			<div class="col-span-4">
				<p class="text-center text-2xl">Material Symbols examples:</p>
				<md-icon>settings</md-icon>
				<md-icon>palette</md-icon>
				<md-icon>home</md-icon>
				<md-icon>person</md-icon>
			</div>
		</div>
	</div>

	<div>
		<Title>List</Title>
		<md-list class="w-full">
			<md-list-item> Fruits </md-list-item>
			<md-divider></md-divider>
			<md-list-item> Apple </md-list-item>
			<md-list-item> Banana </md-list-item>
			<md-list-item>
				<div slot="headline">Cucumber</div>
				<div slot="supporting-text">
					Cucumbers are long green fruits that are just as long as this multi-line description
				</div>
			</md-list-item>
			<md-list-item
				type="link"
				href="https://google.com/search?q=buy+kiwis&tbm=shop"
				target="_blank"
			>
				<div slot="headline">Shop for Kiwis</div>
				<div slot="supporting-text">This will link you out in a new tab</div>
				<md-icon slot="end">open_in_new</md-icon>
			</md-list-item>
		</md-list>
		<HorizontalRule />
	</div>

	<div>
		<Title>Open Modal with dialog</Title>
		<md-filled-button
			onclick={() => demoResourceDialog.show()}
			role="button"
			tabindex="0"
			onkeydown={(event: KeyboardEvent) => event.key === 'Enter' && demoResourceDialog.show()}
			>New</md-filled-button
		>

		<md-dialog id="demoResourceDialog" bind:this={demoResourceDialog} class="w-fill">
			<div slot="headline" class="w-64">Demo Resource</div>
			<form slot="content" id="post-demo-resource" method="POST" class="flex flex-col">
				<md-filled-text-field label="Name" name="name" class="w-full"> </md-filled-text-field>
				<br />
				<md-filled-text-field
					label="Description"
					name="description"
					type="textarea"
					rows="3"
					class="my-3 w-full"
				>
				</md-filled-text-field>
				<md-filled-select label="Language" name="language" class="w-full">
					<md-select-option value="en-US">
						<div slot="headline">en-US</div>
					</md-select-option>
					<md-select-option value="dk-DK">
						<div slot="headline">dk-DK</div>
					</md-select-option>
					<md-select-option value="de-DE">
						<div slot="headline">de-DE</div>
					</md-select-option>
				</md-filled-select>
				<!-- <button>Submit</button> -->
				<!-- <md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button> -->
				<div slot="actions" class="ml-auto py-4">
					<md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button>
					<md-filled-tonal-button
						role="button"
						tabindex="0"
						onclick={(event: Event) => cancelForm(event)}
						onkeydown={(event: KeyboardEvent) => event.key === 'Enter' && cancelForm(event)}
						>Cancel</md-filled-tonal-button
					>
				</div>
			</form>
		</md-dialog>

		<HorizontalRule />
	</div>

	<div>
		<Title>User Form</Title>
		<!-- Applying TailwindCSS classes formats the following paragraph: -->
		<p class="text-center text-2xl">
			(Only the text fields are material design - the div's around are tailwind CSS)
		</p>

		<section class="flex h-full w-full justify-center">
			<div class="center py-12 md:w-8/12 lg:ml-6 lg:w-5/12">
				<div class="border-primary-400 rounded-2xl border-4 bg-blue-50 p-6">
					<form method="POST">
						<!-- Name input -->
						{#if type === 'signup'}
							<div class="relative mb-6">
								<md-filled-text-field
									label="Full name"
									type="input"
									name="name"
									role="textbox"
									tabindex="0"
									class="mr-2 w-full"
								>
								</md-filled-text-field>
							</div>
						{/if}

						<!-- Email input -->
						<div class="relative mb-6">
							<md-filled-text-field
								label="Email address"
								type="email"
								name="email"
								role="textbox"
								tabindex="0"
								class="mr-2 w-full"
							>
							</md-filled-text-field>
						</div>

						<!-- Password input -->
						<div class="relative mb-6">
							<md-filled-text-field
								label="Password"
								type="password"
								name="password"
								role="textbox"
								tabindex="0"
								class="mr-2 w-full"
							>
							</md-filled-text-field>
						</div>

						<!-- Submit button -->
						<div class="text-center">
							<button
								type="submit"
								class="inline-block w-5/6 rounded bg-blue-400 px-7 pb-2.5 pt-3 uppercase leading-normal text-white shadow-[0_4px_9px_-4px_#3b71ca] transition duration-150 ease-in-out hover:bg-blue-700 hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:bg-blue-600 focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:outline-none focus:ring-0 active:bg-blue-700 active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] dark:shadow-[0_4px_9px_-4px_rgba(59,113,202,0.5)] dark:hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)]"
								data-te-ripple-init
								data-te-ripple-color="light"
							>
								{button}
							</button>
						</div>
					</form>
				</div>
			</div>
		</section>

		<HorizontalRule />
	</div>

	<div>
		<Title>Card</Title>

		<div class="grid grid-cols-3 gap-4">
			<md-elevated-card>
				<Title>Elevated Card</Title>
				<p class="text-center text-2xl">Not implemented yet in Material Design 3</p>
			</md-elevated-card>
			<md-filled-card>
				<Title>Filled Card</Title>
				<p class="text-center text-2xl">Not implemented yet in Material Design 3</p>
			</md-filled-card>
			<md-outlined-card>
				<Title>Filled Card</Title>
				<p class="text-center text-2xl">Not implemented yet in Material Design 3</p>
			</md-outlined-card>
		</div>

		<HorizontalRule />
	</div>
</div>

<!-- <JsonData data={theme}></JsonData> -->

<style>
	/* Local override works:  */
	/* #demoResourceDialog {
		--md-dialog-headline-color: #e4a112;
		--md-dialog-container-color: #e5deb9;
	} */
	/* .staticMaterialThemeBuilder {
		@import './dark.css';
		@import './dark-hc.css';
		@import './dark-mc.css';
		@import './light.css';
		@import './light-hc.css';
		@import './light-mc.css';
	} */

	md-icon {
		--md-icon-font: 'Material Symbols Rounded';
		--md-icon-size: 48px;
	}

	#post-demo-resource {
		display: flex;
		flex-direction: column;
	}
	#post-demo-resource md-filled-text-field {
		margin-bottom: 1rem;
	}
	#post-demo-resource md-filled-select {
		margin-bottom: 1rem;
	}
	#post-demo-resource md-filled-button {
		margin-top: 1rem;
	}
	#post-demo-resource md-filled-tonal-button {
		margin-top: 1rem;
	}
</style>
