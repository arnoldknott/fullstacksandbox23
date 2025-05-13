<script lang="ts">
	import { type AppTheme } from '$lib/theming';
	import { hexFromArgb, Hct } from '@material/material-color-utilities';
	import { themeStore } from '$lib/stores';
	import { onDestroy } from 'svelte';

	let { background, color }: { background: string; color: string } = $props();
	const text = background.replace('--md-sys-color-', '').replaceAll('-', ' ');

	let theme = $state({} as AppTheme);
	const unsubscribeThemeStore = themeStore.subscribe((value) => {
		theme = value;
	});

	let colorValueHex = $derived.by(() => {
		if (!theme.currentMode) {
			return '';
		} else {
			let colors = theme[theme.currentMode].colors;
			const variable = background
				.replace('--md-sys-color-', '')
				.replace(/-./g, (x) => x.toUpperCase()[1]) as keyof typeof colors;
			return hexFromArgb(colors[variable]);
		}
	});
	let colorValueHct = $derived.by(() => {
		if (!theme.currentMode) {
			return {
				hue: NaN,
				chroma: NaN,
				tone: NaN
			};
		} else {
			let colors = theme[theme.currentMode].colors;
			const variable = background
				.replace('--md-sys-color-', '')
				.replace(/-./g, (x) => x.toUpperCase()[1]) as keyof typeof colors;
			const chroma = Math.round(Hct.fromInt(colors[variable]).chroma);
			const hue = Math.round(Hct.fromInt(colors[variable]).hue);
			const tone = Math.round(Hct.fromInt(colors[variable]).tone);
			return {
				hue: hue,
				chroma: chroma,
				tone: tone
			};
		}
	});

	onDestroy(() => {
		unsubscribeThemeStore();
	});
</script>

<div class="flex h-32 grow p-2 md:h-24" style="background-color: var({background});">
	<p class="text-left text-sm md:text-base" style="color: var({color});">
		{text}
		<br />
		<!-- Works, but laggy, when dragging the colors: -->
		<code class="text-xs">{colorValueHex}</code>
		<br />
		<span class="text-xs"
			>H: <code>{colorValueHct.hue}</code>, C: <code>{colorValueHct.chroma}</code>, T:
			<code>{colorValueHct.tone}</code></span
		>
		<!-- <code class="text-base">{hexFromArgb(themestore.[themeStore.currentMode]colors[variable])}</code> -->
	</p>
</div>
