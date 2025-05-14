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

<div
	class="flex {debug ? 'h-36 md:h-48' : 'h-30'} m-1 grow rounded-xl p-2 bg-{background} text-{text}"
>
	<div class="flex w-full flex-col overflow-auto">
		<div class="title">{background}</div>
		<div>
			{@render children?.()}
		</div>
		{#if debug}
			<div class="grid md:grid-cols-2">
				<div class="text-sm">Tailwind CSS:</div>
				<code class="text-xs">--color-{background}</code>
				<div class="divider md:col-span-2"></div>
				<div class="text-sm">Material Design:</div>
				<code class="text-xs">{materialDesignVariable}</code>
				<div class="divider md:col-span-2"></div>
				<div class="text-sm">Hex:</div>
				<code class="text-xs">{colorValues.hex}</code>
				<div class="divider md:col-span-2"></div>
				<div class="text-xs">HCT:</div>
				<code class="text-xs"
					>{colorValues.hct.hue}, {colorValues.hct.chroma},{colorValues.hct.tone}</code
				>
				<div class="divider md:col-span-2"></div>
				<div class="text-xs">RGBA:</div>
				<code class="text-xs"
					>{colorValues.rgba.r}, {colorValues.rgba.g}, {colorValues.rgba.b}, {colorValues.rgba
						.a}</code
				>
				<div class="divider md:col-span-2"></div>
			</div>
		{/if}
	</div>
</div>
