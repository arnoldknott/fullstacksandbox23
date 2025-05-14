<script lang="ts">
	import { type AppTheme } from '$lib/theming';
	import { hexFromArgb, Hct, rgbaFromArgb } from '@material/material-color-utilities';
	import { themeStore } from '$lib/stores';
	import { onDestroy, type Snippet } from 'svelte';
	import appCss from '/src/app.css?raw';

	let {
		background,
		text,
		children,
		debug = false
	}: { background: string; text: string; children?: Snippet; debug?: boolean } = $props();
	// const text = background.replace('--md-sys-color-', '').replaceAll('-', ' ');

	let theme = $state({} as AppTheme);
	const unsubscribeThemeStore = themeStore.subscribe((value) => {
		theme = value;
	});

	const findMaterialDesignVariable = (tailwindColorVariable: string): string | null => {
		// Match CSS variable assignments like: --color-background: var(--md-rgb-color-background);
		const regex = new RegExp(`${tailwindColorVariable}:\\s*rgb\\(var\\((--[\\w-]+)\\)\\)`, 'g');
		console.log('=== playground - design - ColorTile - regex ===');
		console.log(regex);
		const match = regex.exec(appCss);

		return match ? match[1] : null;
	};

	const materialDesignVariable = findMaterialDesignVariable(`--color-${background}`);
	const materialDesignColorName = materialDesignVariable
		?.replace('--md-rgb-color-', '')
		.replace(/-./g, (x) => x.toUpperCase()[1]);

	let colorValues = $derived.by(() => {
		if (!theme.currentMode) {
			return {
				hex: '',
				hct: {
					hue: NaN,
					chroma: NaN,
					tone: NaN
				},
				rgba: {
					r: NaN,
					g: NaN,
					b: NaN,
					a: NaN
				}
			};
		} else {
			let colors = theme[theme.currentMode].colors;
			const color = colors[materialDesignColorName as keyof typeof colors];
			return {
				hex: hexFromArgb(color),
				hct: {
					hue: Math.round(Hct.fromInt(color).hue),
					chroma: Math.round(Hct.fromInt(color).chroma),
					tone: Math.round(Hct.fromInt(color).tone)
				},
				rgba: rgbaFromArgb(color)
			};
		}
	});

	onDestroy(() => {
		unsubscribeThemeStore();
	});
</script>

<div class="flex h-36 grow p-2 md:h-40 bg-{background} text-{text}">
	<div class="flex flex-col">
		<div class="title">{background}</div>
		{#if debug}
			<div class="text-left text-sm">
				TailwindCSS: <code class="text-xs">--color-{background}</code>
			</div>
			<div class="text-left text-sm">
				Material Design: <code class="text-xs">{materialDesignVariable}</code>
			</div>
			<div class="text-left text-sm">
				Hex: <code class="text-xs">{colorValues.hex}</code>
				<br />
				<span class="text-xs"
					>HCT: <code>{colorValues.hct.hue}, {colorValues.hct.chroma},{colorValues.hct.tone}</code
					></span
				>
				<br />
				<span class="text-xs"
					>RGBA: <code
						>{colorValues.rgba.r}, {colorValues.rgba.g}, {colorValues.rgba.b}, {colorValues.rgba
							.a}</code
					></span
				>
			</div>
		{/if}
	</div>
	<div>
		{@render children?.()}
	</div>
</div>
