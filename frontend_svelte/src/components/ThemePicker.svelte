<script lang="ts">
	import { Variant, type ColorConfig } from '$lib/theming';

	let { values = $bindable() }: { values: ColorConfig } = $props();

	// let sourceColor = $state(values.sourceColor);
	// let variant = $state(values.variant);
	// let contrast = $state(values.contrast);
	// let variant = $state(Variant.TONAL_SPOT);
	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
	const allContrasts = Array.from(
		{ length: (contrastMax - contrastMin) / contrastStep + 1 },
		(_, i) => contrastMin + i * contrastStep
	);
	// let contrast = $state(0.0);
	// $effect(() => console.log('sourceColor:', sourceColor, 'variant:', variant, 'contrast:', contrast));
</script>

<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
	<div class="w-36 md:w-48">
		<label class="label label-text" for="colorPicker"
			>Source color
			<span class="label">
				<code class="label-text-alt">{values.sourceColor}</code>
			</span>
		</label>
		<input
			class="input"
			type="color"
			id="colorPicker"
			name="color-picker"
			bind:value={values.sourceColor}
		/>
	</div>
	<div class="relative w-36 md:w-48">
		<label class="label label-text" for="themeVariant">Variant</label>
		<select
			class="select select-floating max-w-sm"
			aria-label="Select variant"
			id="themeVariant"
			bind:value={values.variant}
		>
			{#each Object.values(Variant) as variant (variant)}
				<option value={variant}>{variant}</option>
			{/each}
			<!-- <option value="TONAL_SPOT">Tonal Spot</option>
            <option value="MONOCHROME">Monochrome</option>
            <option value="NEUTRAL">Neutral</option>
            <option value="VIBRANT">Vibrant</option>
            <option value="EXPRESSIVE">Expressive</option>
            <option value="FIDELITY">Fidelity</option>
            <option value="CONTENT">Content</option>
            <option value="RAINBOW">Rainbow</option>
            <option value="FRUIT_SALAD">Fruit Salad</option> -->
		</select>
	</div>
	<div class="w-36 md:w-48">
		<label class="label label-text" for="contrast"
			>Contrast: <span class="label">
				<code class="label-text-alt">{values.contrast}</code>
			</span></label
		>

		<input
			type="range"
			min={contrastMin}
			max={contrastMax}
			step={contrastStep}
			class="range w-full"
			aria-label="contrast"
			id="contrast"
			bind:value={values.contrast}
		/>
		<div class="flex w-full justify-between px-2 text-xs">
			{#each allContrasts as _ (_)}
				<span>|</span>
			{/each}
		</div>
	</div>
</div>
