<script lang="ts">
	import { type SubmitFunction } from '@sveltejs/kit';
	import { enhance } from '$app/forms';
	import type { ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';

	let {
		artificialIntelligenceForm = $bindable<HTMLFormElement | null>(),
		updateProfileAccount,
		saveProfileAccount,
		artificialIntelligenceConfiguration = $bindable()
	}: {
		artificialIntelligenceForm: HTMLFormElement | null;
		updateProfileAccount: SubmitFunction;
		saveProfileAccount: () => void;
		artificialIntelligenceConfiguration: ArtificialIntelligenceConfig;
	} = $props();

	const temperatureMin = 0.2;
	const temperatureMax = 1.0;
	const temperatureStep = 0.1;
</script>

<form
	method="POST"
	class="align-between flex h-full flex-col"
	action="/?/putme"
	id="ai-form"
	use:enhance={updateProfileAccount}
	bind:this={artificialIntelligenceForm}
>
	<li class="flex grow items-center gap-2">
		<span class="icon-[mingcute--ai-fill] bg-neutral size-6"></span>
		<span class="text-neutral grow">Artificial Intelligence</span>
	</li>
	<li class="grow">
		<div class="flex w-full flex-row pt-2">
			<label class="label label-text text-base" for="ai-enabled">off</label>
			<input
				type="checkbox"
				class="switch switch-neutral"
				bind:checked={artificialIntelligenceConfiguration.enabled}
				id="ai-enabled"
			/>
			<label class="label label-text text-base" for="ai-enabled"> on</label>
		</div>
	</li>
	<li class="relative w-full grow pt-1">
		<label
			class="label label-text {artificialIntelligenceConfiguration.enabled
				? ''
				: 'text-base-content-variant'}"
			for="ai-model">Model</label
		>
		<select
			class="select select-floating max-w-sm"
			aria-label="Select model"
			id="ai-model"
			name="model-picker"
			disabled={!artificialIntelligenceConfiguration.enabled}
			onchange={() => saveProfileAccount()}
			bind:value={artificialIntelligenceConfiguration.model}
		>
			<option value="Model 1">Model 1</option>
			<option value="Model 2">Model 2</option>
			<option value="Model 3">Model 3</option>
		</select>
	</li>
	<li class="relative w-full pt-2">
		<label
			class="label label-text flex {artificialIntelligenceConfiguration.enabled
				? ''
				: 'text-base-content-variant'}"
			for="ai-temperature"
		>
			<span class="grow">Temperature: </span>
			<code>{artificialIntelligenceConfiguration.temperature}</code>
		</label>
		<input
			type="range"
			min={temperatureMin}
			max={temperatureMax}
			step={temperatureStep}
			class="range {artificialIntelligenceConfiguration.enabled ? '' : 'disabled'} w-full"
			id="ai-temperature"
			name="temperature"
			onchange={() => saveProfileAccount()}
			bind:value={artificialIntelligenceConfiguration.temperature}
		/>
	</li>
</form>
