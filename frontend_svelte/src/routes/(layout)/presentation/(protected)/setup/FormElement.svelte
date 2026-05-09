<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		title,
		children,
		description,
		classes
	}: { title: string; children: Snippet; description?: Snippet; classes?: string } = $props();
</script>

<dl class={classes}>
	<dt>
		<div class="label text-base-content label-large">{title}</div>
		{#if description}
			<p class="ml-5">
				{@render description()}
			</p>
		{/if}
	</dt>
	<dd class="text-base-content mb-5 ml-5">
		{@render children()}
	</dd>
</dl>
