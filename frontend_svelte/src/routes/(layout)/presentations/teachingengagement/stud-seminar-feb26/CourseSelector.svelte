<script lang="ts">
	let {
		label,
		options,
		selectedOptions,
		color = 'info',
		compact = false,
		onSelectAll,
		onSelectNone,
		onToggle
	}: {
		label: string;
		options: string[];
		selectedOptions: string[];
		color?: string;
		compact?: boolean;
		onSelectAll: () => void;
		onSelectNone: () => void;
		onToggle: (option: string) => void;
	} = $props();
</script>

<div class={`flex flex-wrap items-center ${compact ? 'gap-2' : 'gap-3'}`}>
	<span class={`text-base-content/80 font-semibold ${compact ? 'text-2xl' : 'text-4xl'}`}
		>{label}:</span
	>
	<button
		class={`btn ${compact ? 'btn-sm text-xl font-semibold' : 'btn-lg text-2xl font-bold'} btn-${color}`}
		type="button"
		onclick={(event) => {
			event.stopPropagation();
			onSelectAll();
		}}
	>
		All
	</button>
	<button
		class={`btn ${compact ? 'btn-sm text-xl font-semibold' : 'btn-lg text-2xl font-bold'} btn-outline btn-${color}`}
		type="button"
		onclick={(event) => {
			event.stopPropagation();
			onSelectNone();
		}}
	>
		None
	</button>
	{#each options as option (option)}
		<button
			type="button"
			class={`btn ${compact ? 'btn-sm text-xl font-semibold' : 'btn-lg text-2xl font-bold'} ${selectedOptions.includes(option) ? `btn-${color}` : `btn-outline btn-${color}`}`}
			onclick={(event) => {
				event.stopPropagation();
				onToggle(option);
			}}
		>
			{option}
		</button>
	{/each}
</div>
