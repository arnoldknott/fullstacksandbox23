<script lang="ts">
	import type { Snippet } from 'svelte';
	import HelpTooltip from '../../../playground/components/HelpTooltip.svelte';

	let {
		title,
		children,
		description,
		classes
	}: { title: string; children: Snippet; description?: Snippet; classes?: string } = $props();
</script>

<dl class={classes}>
	<dt>
		<div class="label text-base-content label-large">
			{title}
			{#if description}
				<HelpTooltip text={description} />
			{/if}
		</div>
	</dt>
	<dd class="text-base-content mb-5 ml-5">
		{@render children()}
	</dd>
</dl>
