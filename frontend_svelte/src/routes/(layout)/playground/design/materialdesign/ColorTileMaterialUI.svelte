<script lang="ts">
	// import type { AppTheme } from '$lib/theming';
	// import { getContext } from 'svelte';
	import { Hct, hexFromArgb } from '@material/material-color-utilities';
	import { onDestroy } from 'svelte';

	// import { theme } from '../routes/(layout)/layout.svelte'; // TBD: consider moving to $lib/stores?
	import theme from '$lib/stores/theme';
	import { type AppTheme } from '$lib/theming';

	let { background, color }: { background: string; color: string } = $props();
	const text = $derived(background.replace('--md-sys-color-', '').replaceAll('-', ' '));

	let themeState = $state({} as AppTheme);
	const unsubscribeThemeStore = theme.subscribe((value) => {
		// console.log('theme:', value);
		themeState = value;
	});

	let colorValueHex = $derived.by(() => {
		if (!themeState.currentMode) {
			return '';
		} else {
			let colors = themeState[themeState.currentMode].colors;
			const variable = background
				.replace('--md-sys-color-', '')
				.replace(/-./g, (x) => x.toUpperCase()[1]) as keyof typeof colors;
			return hexFromArgb(colors[variable]);
		}
	});
	let colorValueHct = $derived.by(() => {
		if (!themeState.currentMode) {
			return {
				hue: NaN,
				chroma: NaN,
				tone: NaN
			};
		} else {
			let colors = themeState[themeState.currentMode].colors;
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

	// //     // console.log('themeState:', themeState[theme.currentMode].colors['primary']);
	// // });
	// let colorValue = $state()
	// $effect(() => {
	//     if (theme === undefined) return;
	//     let colors = theme[theme.currentMode].colors
	//     const variable = background.replace('--md-sys-color-', '').replace(/-./g, x => x.toUpperCase()[1]) as keyof typeof colors;
	//     // console.log('variable:', variable);
	//     // console.log('color ', variable, ': ', colors[variable])
	//     colorValue = hexFromArgb(colors[variable])
	//     // colorValue = colors[variable]
	// });

	// let theme: AppTheme = $state(getContext('theme'));

	// console.log('variable:', variable);
	// $effect(() => {console.log('color ', variable, ': ', colors[variable])});
	// console.log('theme:', $theme);
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
		<!-- <code class="text-base">{hexFromArgb(theme.[theme.currentMode]colors[variable])}</code> -->
	</p>
</div>
