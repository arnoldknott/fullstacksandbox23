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
    let panes: Pane[] = $state(contents.map((_content) => ({ pane: null as unknown as HTMLDivElement, left: NaN, width: 0, minWidth: 100, maxWidth: 400, resizer: null })));

    const activateResizer = (paneIndex: number) => {
        panes[paneIndex].resizerActive = true;
    };

    const resizePanes = (event: PointerEvent, rightResizingPaneIndex: number) => {
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