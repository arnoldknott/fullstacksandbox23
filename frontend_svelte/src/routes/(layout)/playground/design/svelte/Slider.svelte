<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		name,
		id,
		value = $bindable(),
		min = 0,
		max = 1000,
		step = 100,
		preName
	}: {
		name: string;
		id: string;
		value?: number | undefined;
		min?: number;
		max?: number;
		step?: number;
		preName?: Snippet;
	} = $props();
</script>

<div>
	<label class="label label-text flex justify-between" for={id}
		><div class="flex flex-row">{@render preName?.()}{name}:</div>
		<span class="label">
			<code class="label-text-alt">{value}</code>
		</span></label
	>

	<input
		type="range"
		{min}
		{max}
		{step}
		class="range w-full"
		aria-label={name}
		{id}
		bind:value
		disabled={value === undefined}
	/>
</div>
