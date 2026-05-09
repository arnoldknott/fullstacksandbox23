<script lang="ts">
	import { initTooltip } from '$lib/userInterface';
	import type { Snippet } from 'svelte';

	let { text }: { text: string | Snippet } = $props();

	let tooltip: HTMLElement;
	let tipVisibility = $state(false);
	const toggleTooltip = () => {
		if (tipVisibility) {
			window.HSTooltip.hide(tooltip);
		} else {
			window.HSTooltip.show(tooltip);
		}
		tipVisibility = !tipVisibility;
	};
	// text =
	// 	'Where is the source code for this presentation stored? For example, intern - as part of the source code of this platform - a github or gitlab repository. <span class="text-accent">Consider adding the option for a staging environemnt.</span>';
</script>

<div class="tooltip" bind:this={tooltip} {@attach initTooltip}>
	<button
		class="tooltip-toggle btn-info-container btn-circle btn btn-xs btn-gradient shadow-outline scale-80 align-top shadow-sm"
		onclick={toggleTooltip}
		aria-label="Help"
	>
		<span class="icon-[ic--round-question-mark] bg-info-container-content"></span>
	</button>
	<div class="tooltip-content tooltip-shown:opacity-100 tooltip-shown:visible" role="tooltip">
		<div
			class="tooltip-body bg-info-container text-info-container-content shadow-outline border-info max-w-xs rounded-xl border-[1px] text-pretty shadow"
		>
			{#if typeof text === 'string'}
				{text}
			{:else}
				{@render text()}
			{/if}
			<!-- Where is the source code for this presentation stored? For example, intern - as part of the source
			code of this platform - a github or gitlab repository.
			<span class="text-accent">Consider adding the option for a staging environemnt.</span> -->
		</div>
	</div>
</div>
