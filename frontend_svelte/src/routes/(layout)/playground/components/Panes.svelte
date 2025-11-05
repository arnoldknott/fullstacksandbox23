<script lang="ts">
	// import JsonData from '$components/JsonData.svelte';
	import { type Snippet } from 'svelte';
	export type PaneInputs = {
		id: string;
		content: Snippet;
		minWidth?: number;
		maxWidth?: number;
	};
	// export type PaneAPI = {
	// 	closePane: (paneIndex: string) => void;
	// };
	let { inputs, closePane }: { inputs: PaneInputs[]; closePane?: (paneId: string) => void } =
		$props();

	type Pane = PaneInputs & {
		pane: HTMLDivElement;
		// content: Snippet;
		left: number;
		width: number;
		// minWidth?: number;
		// maxWidth?: number;
		resizer?: HTMLDivElement | null;
		// set active for the right pane of the pair, that is currently being resized.
		resizerActive?: boolean;
	};
	let panes: Pane[] = $state(
		inputs.map((input) => ({
			id: input.id,
			pane: null as unknown as HTMLDivElement,
			content: input.content,
			left: NaN,
			width: 0,
			minWidth: input.minWidth,
			maxWidth: input.maxWidth,
			resizer: null
		}))
	);
	$effect(() => {
		// Keep only panes that still exist in inputs
		// panes = panes.filter((pane) => inputs.some((input) => input.id === pane.id));
	});

	const activateResizer = (paneIndex: number) => {
		panes[paneIndex].resizerActive = true;
	};

	const resizePanes = (event: PointerEvent, rightResizingPaneIndex: number) => {
		// console.log('Resizing panes at index:', rightResizingPaneIndex);
		// assing the panes involved:
		const leftPane = panes[rightResizingPaneIndex - 1];
		const rightPane = panes[rightResizingPaneIndex];
		// update left in inforamtion in both panes (needs initialization)
		leftPane.left = leftPane.pane.getBoundingClientRect().left;
		rightPane.left = rightPane.pane.getBoundingClientRect().left;
		// Keep only the two adjacent panes affected by this resizer.
		// Maintain their combined width constant during the drag.
		const pairTotalWidth = leftPane.width + rightPane.width; // capture BEFORE updating either
		const minLeft = leftPane.minWidth ?? 0;
		const maxLeft = leftPane.maxWidth ?? Infinity;
		const minRight = rightPane.minWidth ?? 0;
		const maxRight = rightPane.maxWidth ?? Infinity;
		// Left must be within its own [minLeft, maxLeft]
		// and also satisfy right constraints:
		//  - right >= minRight  -> left <= pairTotalWidth - minRight
		//  - right <= maxRight  -> left >= pairTotalWidth - maxRight
		let leftLowerBound = Math.max(minLeft, pairTotalWidth - maxRight);
		let leftUpperBound = Math.min(maxLeft, pairTotalWidth - minRight);
		if (leftLowerBound > leftUpperBound) {
			// If constraints contradict, collapse to nearest feasible value
			leftUpperBound = leftLowerBound;
		}
		// Compute left pane candidate width from absolute pointer position
		const leftCandidate = event.clientX - leftPane.left;
		// Clamp left within derived bounds
		leftPane.width = Math.max(leftLowerBound, Math.min(leftCandidate, leftUpperBound));
		// Right width is whatever remains from the pair total (no resizer width involved here)
		rightPane.width = pairTotalWidth - leftPane.width;
	};
</script>

<svelte:window
	onpointermove={(event) => {
		if (panes.some((pane) => pane.resizerActive)) {
			resizePanes(
				event,
				panes.findIndex((pane) => pane.resizerActive)
			);
		}
	}}
	onpointerup={() => panes.forEach((pane) => (pane.resizerActive = false))}
/>

{#snippet resizer(paneIndex: number)}
	<div
		class="resizer bg-base-200 flex h-full w-3 cursor-col-resize items-center justify-center"
		role="button"
		aria-label="Resizing panes"
		tabindex="0"
		onpointerdown={() => activateResizer(paneIndex)}
		bind:this={panes[paneIndex].resizer}
	>
		<div
			class="resizer-handle {panes[paneIndex].resizerActive
				? 'bg-outline'
				: 'bg-outline-variant'} h-20 w-1 rounded-full"
		></div>
	</div>
{/snippet}

<div class="bg-base-200 mt-10 flex flex-col rounded-2xl">
	<div class="flex h-screen w-full p-4">
		{#each panes as pane, i (pane.id)}
			<div
				class="bg-base-250 grow overflow-y-scroll rounded-xl"
				bind:this={pane.pane}
				bind:clientWidth={pane.width}
				style:width={pane.width + 'px'}
			>
				{#if closePane}
					<div class="flex justify-end">
						<button
							class=" btn btn-text btn-sm btn-circle"
							aria-label="Close Button"
							onclick={() => closePane(pane.id)}
						>
							<span class="icon-[tabler--x] size-5"></span>
						</button>
					</div>
				{/if}
				<!-- Degugging inforamtion of pane: -->
				<div class="label-small flex flex-col">
					<div class="label">Left: {pane.left} px</div>
					<div class="label">Width: {pane.width} px</div>
					<div class="label">MinWidth: {pane.minWidth} px</div>
					<div class="label">MaxWidth: {pane.maxWidth} px</div>
					<div class="label">ResizerActive: {pane.resizerActive ? 'true' : 'false'}</div>
				</div>
				{@render pane.content?.()}
			</div>

			{#if i !== panes.length - 1}
				{@render resizer(i + 1)}
			{/if}
		{/each}
	</div>
</div>
