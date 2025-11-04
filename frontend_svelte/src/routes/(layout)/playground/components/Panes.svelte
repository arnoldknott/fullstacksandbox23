<script lang="ts">
	import JsonData from "$components/JsonData.svelte";
    import { type Snippet } from "svelte"
    let {contents}: {contents: Snippet[]} = $props();

    type Pane = {
		pane: HTMLDivElement;
		left: number;
		width: number;
		minWidth?: number;
		maxWidth?: number;
		resizer?: HTMLDivElement | null;
		// set active for the right pane of the pair, that is currently being resized.
		resizerActive?: boolean;
	};
    let panes: Pane[] = $state(contents.map((_content) => ({ pane: null as unknown as HTMLDivElement, left: NaN, width: 0, minWidth: 100, maxWidth: 300, resizer: null })));

    const activateResizer = (paneIndex: number) => {
        panes[paneIndex].resizerActive = true;
    };

    const resizePanes = (event: PointerEvent, rightResizingPaneIndex: number) => {
        // console.log("resizePanes", rightResizingPaneIndex, event.clientX);
        // assing the panes involved:
        const leftPane = panes[rightResizingPaneIndex - 1];
        const rightPane = panes[rightResizingPaneIndex ];
        // update left in inforamtion in both panes (needs initialization)
		leftPane.left = leftPane.pane.getBoundingClientRect().left;
		rightPane.left = rightPane.pane.getBoundingClientRect().left;
        // Keep only the two adjacent panes affected by this resizer.
        // Maintain their combined width constant during the drag.
        const pairTotalWidth = leftPane.width + rightPane.width; // capture BEFORE updating either
        const minLeft = leftPane.minWidth ?? 0;
        const maxLeft = leftPane.maxWidth ?? Infinity;
        const minRight = rightPane.minWidth ?? 0;
        // TBD: implment the static maxWidth if specified:
        const maxRight = rightPane.maxWidth ?? Infinity;
        const boundLeft = Math.min(
            maxLeft,
            Math.max(minLeft, pairTotalWidth - minRight)
        );
        // Compute left pane candidate width from absolute pointer position
        const leftCandidate = event.clientX - leftPane.left;
        // Clamp left width between its min and the max that preserves the right min
        leftPane.width = Math.max(minLeft, Math.min(leftCandidate, boundLeft));
        // Right width is whatever remains from the pair total (no resizer width involved here)
        rightPane.width = pairTotalWidth - leftPane.width;
        // console.log("leftPane.width", leftPane.width, "rightPane.width", rightPane.width);
        // console.log("leftPaneWidthDirect", panes[rightResizingPaneIndex - 1].width);
        // console.log("rightPaneWidthDirect", rightPane.width);
		// if (triplePaneContainer) {
		// 	const rect = triplePaneContainer.getBoundingClientRect();
		// 	const totalInner = rect.width - 2 * resizerWidth; // space available for the three panes only

		// 	if (resizeLeftTriplePanesActive) {
		// 		// Dragging the left resizer: adjust Left and Center, keep Right constant
		// 		const x = event.clientX - rect.left; // position from left edge
		// 		const maxLeft = totalInner - triplePaneRightWidth - minPane; // ensure center >= min
		// 		triplePaneLeftWidth = Math.max(minPane, Math.min(x, Math.max(minPane, maxLeft)));
		// 		triplePaneCenterWidth = totalInner - triplePaneLeftWidth - triplePaneRightWidth;
		// 	} else if (resizeRightTriplePanesActive) {
		// 		// Dragging the right resizer: adjust Center and Right, keep Left constant
		// 		const x = event.clientX - rect.left; // position from left edge
		// 		const rightCandidate = rect.width - x - resizerWidth; // width from resizer to right edge
		// 		const maxRight = totalInner - triplePaneLeftWidth - minPane; // ensure center >= min
		// 		triplePaneRightWidth = Math.max(
		// 			minPane,
		// 			Math.min(rightCandidate, Math.max(minPane, maxRight))
		// 		);
		// 		triplePaneCenterWidth = totalInner - triplePaneLeftWidth - triplePaneRightWidth;
		// 	}
		// }
	};

</script>

<svelte:window
	onpointermove={(event) => {
        if (panes.some(pane => pane.resizerActive)) {
            resizePanes(event, panes.findIndex((pane) => pane.resizerActive));
    }
    }}
	onpointerup={() => panes.forEach(pane => pane.resizerActive = false)}
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
    <div class="flex h-80 w-full p-4">
        {#each panes as pane, i}
            <div
                class="grow bg-base-250"
                bind:this={pane.pane}
                bind:clientWidth={pane.width}
                style:width={pane.width + 'px'}
            >
                {@render contents[i]?.()}
                <p>Left: {pane.left} px</p>
                <p>Width: {pane.width} px</p>
                <p>MinWidth: {pane.minWidth} px</p>
                <p>MaxWidth: {pane.maxWidth} px</p>
                <p>ResizerActive: {pane.resizerActive ? 'true' : 'false'}</p>
                <p>Resizer.width: {pane.resizer?.clientWidth || 12} px</p>
                <JsonData data={$state.snapshot(pane.left)} />
            </div>
            {#if i !== panes.length - 1}
                {@render resizer(i + 1)}
            {/if}
        {/each}
    </div>
</div>