<script lang="ts">
	let {
		name,
		id,
		value = $bindable(0),
		min = 0,
		max = 1000,
		step = 100
	}: {
		name: string;
		id: string;
		value?: number;
		min?: number;
		max?: number;
		step?: number;
	} = $props();
</script>

<div>
	<label class="label label-text flex justify-between" for={id}
		>{name}:
		<span class="label">
			<code class="label-text-alt">{value}</code>
		</span></label
	>
	<input type="range" {min} {max} {step} class="range w-full" aria-label={name} {id} bind:value />
</div>
