<script lang="ts">
	import { onMount } from 'svelte';
	import Title from '$components/Title.svelte';

	onMount(async () => {
		const te = await import('tw-elements');
		te.initTWE(
			{ MultiRangeSlider: te.MultiRangeSlider },
			{ allowReinits: true, checkOtherImports: true }
		);
	});

	$: sliderValue = 0;
	$: color = `hsl(${sliderValue * 1.2}, 80%, 80%)`;

	$: sliders = [0, 0, 0, 0];
	$: colors = [
		`hsl(${sliders[0] * 1.2}, 80%, 80%)`,
		`hsl(${sliders[1] * 1.2}, 80%, 80%)`,
		`hsl(${sliders[2] * 1.2}, 80%, 80%)`,
		`hsl(${sliders[3] * 1.2}, 80%, 80%)`
	];
</script>

<!-- <div class="px-10">
    <label
        for="customRange1"
        class="mb-2 inline-block text-primary-700 dark:text-primary-300"
        >Status</label
    >
    <input
        type="range"
        data-te-tooltip="true"
        class="transparent h-[4px] w-full cursor-pointer appearance-none border-transparent bg-neutral-200 dark:bg-neutral-600"
        id="customRange1" />
</div> -->

<Title>Status slider</Title>

<div
	data-twe-multi-range-slider-init
	data-twe-tooltip="true"
	data-twe-number-of-ranges="1"
	on:valueChanged.te.multiRangeSlider={(e) => (sliderValue = e.values.rounded)}
	class="p-10"
>
	{sliderValue}
</div>

<div class="w-100 m-10 p-10" style="background-color: {color};">
	STATUS: {sliderValue}
</div>

<Title>Multiple status sliders</Title>

<div
	data-twe-multi-range-slider-init
	data-twe-tooltip="true"
	data-twe-number-of-ranges="1"
	on:valueChanged.te.multiRangeSlider={(e) => (sliders[0] = e.values.rounded)}
	class="p-10"
>
	Left of Topic 1: {sliders[0]}
</div>

<div
	data-twe-multi-range-slider-init
	data-twe-tooltip="true"
	data-twe-number-of-ranges="1"
	on:valueChanged.te.multiRangeSlider={(e) => (sliders[1] = e.values.rounded)}
	class="p-10"
>
	Between topic 1 and 2: {sliders[1]}
</div>

<div
	data-twe-multi-range-slider-init
	data-twe-tooltip="true"
	data-twe-number-of-ranges="1"
	on:valueChanged.te.multiRangeSlider={(e) => (sliders[2] = e.values.rounded)}
	class="p-10"
>
	Between topic 2 and 3: {sliders[2]}
</div>

<div
	data-twe-multi-range-slider-init
	data-twe-tooltip="true"
	data-twe-number-of-ranges="1"
	on:valueChanged.te.multiRangeSlider={(e) => (sliders[3] = e.values.rounded)}
	class="p-10"
>
	Right of topic 3: {sliders[3]}
</div>

<!-- {#each colors as color, i}
    <div class="w-100 m-10 p-10" style="background-color: {color};">
        STATUS: {sliders[i]}
    </div>
{/each} -->

<!-- TBD: change to Tailwind rows and columns -->
<!-- TBD: change to Tailwind gradients: https://tailwindcss.com/docs/gradient-color-stops#starting-color ?-->
<div class="w-100 m-10 flex">
	<div
		class="flex h-20 w-1/3 items-center justify-center text-2xl"
		style="background: linear-gradient(to right, {colors[0]}, {colors[1]});"
	>
		Topic 1
	</div>
	<div
		class="flex h-20 w-1/3 items-center justify-center text-2xl"
		style="background: linear-gradient(to right, {colors[1]}, {colors[2]});"
	>
		Topic 2
	</div>
	<div
		class="flex h-20 w-1/3 items-center justify-center text-2xl"
		style="background: linear-gradient(to right, {colors[2]}, {colors[3]});"
	>
		Topic 3
	</div>
</div>

<Title>Nice Tailwind CSS gradient</Title>

<div class="w-100 m-10 bg-gradient-to-r from-cyan-500 to-blue-500 p-10">STATUS:</div>
