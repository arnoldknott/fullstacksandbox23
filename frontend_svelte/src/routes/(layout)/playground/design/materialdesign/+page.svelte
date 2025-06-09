<script lang="ts">
	import ColorTileMaterialUi from './ColorTileMaterialUI.svelte';
	import Heading from '$components/Heading.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { themeStore } from '$lib/stores';
	import type { AppTheme } from '$lib/theming';
	import { onDestroy } from 'svelte';
	import { Hct, hexFromArgb } from '@material/material-color-utilities';

	let showSections = $state({
		colors: true,
		palettes: true,
		typography: true,
		shapes: true,
		sliders: true
	});

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

	let palettesArray = $derived(
		palettes
			? Object.entries(palettes).map(([key, value]) => {
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

	onDestroy(() => {
		unsbscribeThemeStore();
	});
</script>

<!-- <JsonData data={palettesArray} /> -->
<!-- <JsonData data={theme} /> -->

<div class="grid w-full grid-cols-1 gap-4 xl:grid-cols-2">
	<div class="xl:col-span-2">
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
		<Heading>Palettes</Heading>
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
			{#each palettesArray as palette (palette.name)}
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

	<div>
		<Heading>Typography</Heading>
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
		<Heading>Shapes (styles)</Heading>
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
				<!-- {#each ['none', 'sm', '', 'md', 'lg', 'xl', '2xl', '3xl', 'full'] as style}
					<div
						class="m-2 w-24 bg-primary-container p-2 text-center text-base md:text-xl rounded-{style}"
					>
						{style}
					</div>
				{/each} -->
				<div
					class="bg-primary-container m-2 w-24 rounded-none p-2 text-center text-base md:text-xl"
				>
					none
				</div>
				<div class="bg-primary-container m-2 w-24 rounded-xs p-2 text-center text-base md:text-xl">
					sm
				</div>
				<div
					class="bg-primary-container m-2 w-24 rounded-sm p-2 text-center text-base md:text-xl"
				></div>
				<div class="bg-primary-container m-2 w-24 rounded-md p-2 text-center text-base md:text-xl">
					md
				</div>
				<div class="bg-primary-container m-2 w-24 rounded-lg p-2 text-center text-base md:text-xl">
					lg
				</div>
				<div class="bg-primary-container m-2 w-24 rounded-xl p-2 text-center text-base md:text-xl">
					xl
				</div>
				<div class="bg-primary-container m-2 w-24 rounded-2xl p-2 text-center text-base md:text-xl">
					2xl
				</div>
				<div class="bg-primary-container m-2 w-24 rounded-3xl p-2 text-center text-base md:text-xl">
					3xl
				</div>
				<div
					class="bg-primary-container m-2 w-24 rounded-full p-2 text-center text-base md:text-xl"
				>
					full
				</div>
			</div>
		</div>
	</div>
</div>
