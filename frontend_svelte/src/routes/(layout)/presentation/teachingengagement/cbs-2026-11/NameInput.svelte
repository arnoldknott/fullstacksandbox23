<script lang="ts">
	let { name = $bindable('') }: { name?: string } = $props();
	const inputId = $props.id();
</script>

<div class="input-filled input-secondary w-full">
	<input type="text" placeholder="" class="input" name="name" id={inputId} bind:value={name} />
	<label class="input-filled-label" for={inputId}>Name:</label>
</div>
