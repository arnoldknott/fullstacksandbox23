<script lang="ts">
	import { hexFromArgb } from '@material/material-color-utilities';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';

	import { Button } from '$components/shadcn/button';
	import { Slider } from '$components/shadcn/slider';
	import Title from '$components/Title.svelte';
	import { themeStore } from '$lib/stores';
	import { Theming } from '$lib/theming';
	// import { afterNavigate } from '$app/navigation';

	let initialSuccessColor = [256, 256, 0]; // Default to green if no theme is set

	onMount(() => {
		$effect(() => {
			const storedTheme = get(themeStore);
			if (storedTheme.currentMode === 'dark') {
				const successColor = Theming.rgbFromHex(hexFromArgb(storedTheme.dark.colors.success)).split(
					' '
				);
				initialSuccessColor = [
					parseInt(successColor[0]),
					parseInt(successColor[1]),
					parseInt(successColor[2])
				];
				color = `rgb(${successColor[0]}, ${successColor[1]}, ${successColor[2]})`;
			} else {
				const successColor = Theming.rgbFromHex(
					hexFromArgb(storedTheme.light.colors.success)
				).split(' ');
				initialSuccessColor = [
					parseInt(successColor[0]),
					parseInt(successColor[1]),
					parseInt(successColor[2])
				];
				color = `rgb(${successColor[0]}, ${successColor[1]}, ${successColor[2]})`;
			}
		});
		return () => {
			document.documentElement.style.setProperty(
				'--color-success',
				`rgb(${initialSuccessColor[0]}, ${initialSuccessColor[1]}, ${initialSuccessColor[2]})`
			);
		};
	});

	let red = $state(128);
	let green = $state(256);
	let blue = $state(128);

	let color = $derived(`rgb(${red}, ${green}, ${blue})`);
	// immitates the behaviour from the dynamic update via themeing:
	$effect(() => {
		document.documentElement.style.setProperty('--color-success', color);
		// const storedTheme = get(themeStore);
		// console.log('=== stored theme - dark-color===');
		// console.log(storedTheme);
	});

	// afterNavigate(() => {
	//     const storedTheme = get(themeStore);
	//     if (storedTheme.currentMode === 'dark') {
	//         const successColor = Theming.rgbFromHex(hexFromArgb(storedTheme.dark.colors.success)).split(
	//             ' '
	//         );
	//         color = `rgb(${successColor[0]}, ${successColor[1]}, ${successColor[2]})`;
	//     } else {
	//         const successColor = Theming.rgbFromHex(
	//             hexFromArgb(storedTheme.light.colors.success)
	//         ).split(' ');
	//         color = `rgb(${successColor[0]}, ${successColor[1]}, ${successColor[2]})`;
	//     }
	// });
</script>

<Title id="integration">Integration</Title>
<p class="m-4">
	Using a shadcn button with tailwindcss classes, that are synchronized with Flyonui colors and
	calculated by Material Design color scheme
</p>

<Button class="bg-accent text-accent-content">Accent Button coupled to Material Design</Button>
<Title id="responsiveness">Responsiveness</Title>
<p class="m-4">
	Testing the responsiveness of the shadcn button with tailwindcss classes, if the theming can be
	obeyed.
</p>

<Button
	class="bg-success text-error-container"
	onclick={() => {
		red = 128;
		green = 256;
		blue = 128;
	}}>Shadcn Button to reset colors</Button
>
<br />
R: {red}
G: {green}
B: {blue}
<Slider class="m-6 w-64" min={0} max={256} step={1} type="single" bind:value={red} />
<Slider class="m-6 w-64" min={0} max={256} step={1} type="single" bind:value={green} />
<Slider class="m-6 w-64" min={0} max={256} step={1} type="single" bind:value={blue} />
<div style="color: var(--my-color-variable);">This text is the calculated color.</div>
<div class="bg-success">
	TailwindCSS color for Material Design "success" - overwritten by local values.
</div>

<Title id="flyonui-classes">FlyonUI classes</Title>
<p class="m-4">Adding FlyonUI classes to the shadcn button for consistent styling.</p>

<Button class="text-primary-content btn btn-gradient btn-primary">Primary Gradient</Button>
<Button class="text-primary-content btn hover:btn-gradient btn-primary"
	>Primary Gradient only on hover</Button
>
