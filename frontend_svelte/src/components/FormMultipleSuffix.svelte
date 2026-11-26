<script lang="ts">
	import FormElement from '$components/FormElement.svelte';

	let { entityLabel, suffix = $bindable('') }: { entityLabel: string; suffix?: string } = $props();

	let multiplePending = $state(false);
	let multipleSuffixes = $state({ start: 1, end: 2 });
	$effect(() => {
		if (multipleSuffixes.end <= multipleSuffixes.start) {
			multipleSuffixes.end = multipleSuffixes.start + 1;
		}
		suffix = multiplePending
			? '_[' + multipleSuffixes.start + ':' + multipleSuffixes.end + ']'
			: '';
	});
</script>

<FormElement title={`Add multiple ${entityLabel}s`}>
	<div class="mb-2 flex flex-1 flex-row items-center gap-1">
		<label class="label label-text text-base-content" for={`new-${entityLabel}-multiple`}>
			<input
				id={`new-${entityLabel}-multiple`}
				type="checkbox"
				disabled
				class="checkbox checkbox-primary"
				bind:checked={multiplePending}
			/>
		</label>
		with suffixes
		<input
			id={`${entityLabel}-multiple-start`}
			type="number"
			placeholder={multipleSuffixes.start.toString()}
			class="input shadow-shadow flex-2 shadow-inner"
			name={`${entityLabel}-multiple-suffix-start`}
			disabled={!multiplePending}
			bind:value={multipleSuffixes.start}
		/>
		<span class="label flex-1"> to</span>
		<input
			id={`${entityLabel}-multiple-end`}
			type="number"
			placeholder={multipleSuffixes.end.toString()}
			class="input shadow-shadow flex-2 shadow-inner"
			name={`${entityLabel}-multiple-suffix-end`}
			disabled={!multiplePending}
			bind:value={multipleSuffixes.end}
		/>
	</div>
	<div class="label">
		<span class="icon-[fluent-color--warning-24] size-4"></span>
		Creation of multiple not functional yet
	</div>
</FormElement>
