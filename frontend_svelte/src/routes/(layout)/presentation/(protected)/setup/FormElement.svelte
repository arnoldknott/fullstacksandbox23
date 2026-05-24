<script lang="ts">
	import type { Snippet } from 'svelte';

	import HelpTooltip from '../../../playground/components/HelpTooltip.svelte';

	let {
		title,
		children,
		description,
		extraClasses
	}: { title: string; children: Snippet; description?: Snippet; extraClasses?: string } = $props();
</script>

<dl class={extraClasses}>
	<dt>
		<div class="title text-base-content">
			{title}
			{#if description}
				<HelpTooltip text={description} />
			{/if}
		</div>
	</dt>
	<dd class="text-base-content-variant mb-5 ml-5">
		{@render children()}
	</dd>
</dl>
