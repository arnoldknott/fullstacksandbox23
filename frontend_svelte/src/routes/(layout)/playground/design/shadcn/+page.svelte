<script lang="ts">
	import { Button } from '$components/shadcn/button';
	import { Slider } from '$components/shadcn/slider';

	let red = $state(128);
	let green = $state(256);
	let blue = $state(128);

	const color = $derived(`rgb(${red}, ${green}, ${blue})`);
	// immitates the behaviour from the dynamic update via themeing:
	$effect(() => {
		document.documentElement.style.setProperty('--color-success', color);
	});
</script>

<Button
	class="bg-success text-error-container"
	onclick={() => {
		red = 128;
		green = 256;
		blue = 128;
	}}>Shadcn Button to reset colors</Button
>
<Button class="bg-accent text-accent-content">Accent Button coupled to Material Design</Button>
<br />
R: {red}
G: {green}
B: {blue}
<Slider
	class="m-6 w-64"
	min={0}
	max={256}
	step={1}
	type="single"
	bind:value={red}
	onValueChange={(next) => {
		console.log('Slider value:', next);
	}}
/>
<Slider
	class="m-6 w-64"
	min={0}
	max={256}
	step={1}
	type="single"
	bind:value={green}
	onValueChange={(next) => {
		console.log('Slider value:', next);
	}}
/>
<Slider
	class="m-6 w-64"
	min={0}
	max={256}
	step={1}
	type="single"
	bind:value={blue}
	onValueChange={(next) => {
		console.log('Slider value:', next);
	}}
/>
<div style="color: var(--my-color-variable);">This text is the calculated color.</div>
<div class="bg-success">
	TailwindCSS color for Material Design "success" - overwritten by local values.
</div>
