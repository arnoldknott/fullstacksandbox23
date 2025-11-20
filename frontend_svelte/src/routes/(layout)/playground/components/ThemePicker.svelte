<script lang="ts">
	import { type SubmitFunction } from '@sveltejs/kit';
	import { enhance } from '$app/forms';
	import { Variant, type ColorConfig } from '$lib/theming';

	let {
		themeForm = $bindable<HTMLFormElement | null>(),
		updateProfileAccount,
		saveProfileAccount,
		mode = $bindable<'light' | 'dark'>(),
		themeConfiguration = $bindable()
	}: {
		themeForm: HTMLFormElement | null;
		updateProfileAccount: SubmitFunction;
		saveProfileAccount: () => void;
		mode: 'light' | 'dark';
		themeConfiguration: ColorConfig;
	} = $props();

	const toggleMode = () => {
		mode = mode === 'dark' ? 'light' : 'dark';
	};

	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
</script>

<form
	method="POST"
	action="/?/putme"
	id="theme-form"
	use:enhance={updateProfileAccount}
	bind:this={themeForm}
>
	<li class="flex items-center gap-2">
		<span class="icon-[material-symbols--palette-outline] bg-secondary size-6"></span>
		<span class="text-secondary grow"> Theming</span>
		<button aria-label="modeToggler" type="button">
			<label for="mode-toggler" class="swap swap-rotate">
				<input id="mode-toggler" type="checkbox" onclick={toggleMode} />
				<span class="icon-[tabler--moon] swap-on size-6"></span>
				<span class="icon-[tabler--sun] swap-off size-6"></span>
			</label>
		</button>
	</li>
	<li>
		<div class="w-full pt-2">
			<label class="label label-text flex" for="color-picker">
				<span class="grow">Source color:</span>
				<code>{themeConfiguration.sourceColor}</code>
			</label>
			<input
				class="w-full"
				type="color"
				id="color-picker"
				name="color-picker"
				onchange={() => saveProfileAccount()}
				bind:value={themeConfiguration.sourceColor}
			/>
		</div>
	</li>
	<li>
		<div class="relative w-full pt-1">
			<label class="label label-text" for="theme-variant">Variant</label>
			<select
				class="select select-floating max-w-sm"
				aria-label="Select variant"
				id="theme-variant"
				name="variant-picker"
				onchange={() => saveProfileAccount()}
				bind:value={themeConfiguration.variant}
			>
				<option value={Variant.TONAL_SPOT}>Tonal Spot</option>
				<!-- <option value={Variant.MONOCHROME}>Monochrome</option> -->
				<option value={Variant.NEUTRAL}>Neutral</option>
				<option value={Variant.VIBRANT}>Vibrant</option>
				<!-- <option value={Variant.EXPRESSIVE}>Expressive</option> -->
				<option value={Variant.FIDELITY}>Fidelity</option>
				<option value={Variant.CONTENT}>Content</option>
				<option value={Variant.RAINBOW}>Rainbow</option>
				<!-- <option value={Variant.FRUIT_SALAD}>Fruit Salad</option> -->
			</select>
		</div>
	</li>
	<li>
		<div class="w-full pt-2">
			<label class="label label-text flex" for="contrast">
				<span class="grow">Contrast: </span>
				<code>{themeConfiguration.contrast}</code>
			</label>

			<input
				type="range"
				min={contrastMin}
				max={contrastMax}
				step={contrastStep}
				class="range w-full"
				aria-label="contrast"
				name="contrast"
				id="contrast"
				onchange={() => saveProfileAccount()}
				bind:value={themeConfiguration.contrast}
			/>
			<!-- <div class="flex w-full justify-between px-2 text-xs">
                    {#each allContrasts as _}
                        <span>|</span>
                    {/each}
                </div> -->
		</div>
	</li>
</form>
