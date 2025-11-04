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
    let panes: Pane[] = $state(contents.map((_content) => ({ pane: null as unknown as HTMLDivElement, left: NaN, width: 0, resizer: null })));

    const activateResizer = (paneIndex: number) => {
        console.log("activateResizer", paneIndex);
        panes[paneIndex].resizerActive = true;
    };

    const resizePanes = (event: PointerEvent, rightResizingPaneIndex: number) => {
        // console.log("resizePanes", rightResizingPaneIndex, event.clientX);
        // assing the panes involved:
        const leftPane = panes[rightResizingPaneIndex - 1];
        const rightPane = panes[rightResizingPaneIndex];
        // update left in inforamtion in both panes (needs initialization)
		leftPane.left = leftPane.pane.getBoundingClientRect().left;
		rightPane.left = rightPane.pane.getBoundingClientRect().left;
        // console.log("leftPane.left", leftPane.left);
        const resizerWidth = rightPane?.resizer?.clientWidth || 12;
        // Compute left pane width from absolute mouse position
        const left = event.clientX - leftPane.left;
        // Setting upper boundary for left pane:
        // ensure right pane >= ( minPane + space for resizer )
        // equals lower boundary for right pane:
        const leftMax = Math.min(left, leftPane.left - (rightPane.minWidth || 0) - resizerWidth);
        // sets a lower boundary for the left pane
        // equals upper boundary for right pane:
        leftPane.width = Math.max((leftPane.minWidth || 0), leftMax);
        const bothPanesWidth = leftPane.width + rightPane.width;
        rightPane.width = bothPanesWidth - leftPane.width - resizerWidth;
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
            const activeResizer = panes.findIndex((pane) => pane.resizerActive);
            console.log("pointermove activeResizer", activeResizer);
            resizePanes(event, activeResizer);
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