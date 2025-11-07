<script lang="ts">
	import { type Snippet } from 'svelte';
	import { SvelteMap } from 'svelte/reactivity';
	export type PaneData = {
		id: string;
		content: Snippet;
		minWidth?: number;
		maxWidth?: number;
	};
	let { panesData, closePane }: { panesData: PaneData[]; closePane?: (paneId: string) => void } =
		$props();

	type PaneSettings = {
		paneIndex: number;
		left: number;
		width: number;
		resizerElement?: HTMLDivElement | null;
		resizerActive?: boolean;
	};

	let panesSettings: SvelteMap<string, PaneSettings> = new SvelteMap<string, PaneSettings>();

    const setPanesSettings = (paneId: string, settings: Partial<PaneSettings>) => {
        panesSettings.set(paneId, {
            ...panesSettings.get(paneId)!,
            ...settings
        });
    }

	let paneElements: SvelteMap<string, HTMLDivElement> = new SvelteMap<string, HTMLDivElement>();

	$effect(() => {
		panesData.forEach((paneData, index) => {
			panesSettings.set(paneData.id, {
				paneIndex: index,
				left: NaN,
				width: 300,
				resizerElement: null,
				resizerActive: false
			});
		});
	});

	const activateResizer = (paneId: string) => {
        setPanesSettings(paneId, {resizerActive: true});
	};

	const resizePanes = (event: PointerEvent, rightResizingPaneIndex: number) => {
		const keyValues = panesSettings.entries();
		let leftId = '';
		let rightId = '';
		for (const [key, pane] of keyValues) {
			if (pane.paneIndex === rightResizingPaneIndex - 1) {
				leftId = key;
			}
			if (pane.paneIndex === rightResizingPaneIndex) {
				rightId = key;
			}
		}
		const leftPaneData = panesData[rightResizingPaneIndex - 1];
		const rightPaneData = panesData[rightResizingPaneIndex];

		// update left in inforamtion in both panes (needs initialization)
		const leftPaneElement = paneElements.get(leftId);
		const rightPaneElement = paneElements.get(rightId);
        setPanesSettings(leftId, {left: leftPaneElement?.getBoundingClientRect().left ?? 0});
        setPanesSettings(rightId, {left: rightPaneElement?.getBoundingClientRect().left ?? 0});
		const leftPane = panesSettings.get(leftId)!;
		const rightPane = panesSettings.get(rightId)!;
		// Keep only the two adjacent panes affected by this resizer.
		// Maintain their combined width constant during the drag.
		const pairTotalWidth = leftPane.width + rightPane.width; // capture before updating either
		const minLeft = leftPaneData.minWidth ?? 0;
		const maxLeft = leftPaneData.maxWidth ?? Infinity;
		const minRight = rightPaneData.minWidth ?? 0;
		const maxRight = rightPaneData.maxWidth ?? Infinity;
		// Left must be within its own [minLeft, maxLeft]
		// and also satisfy right constraints:
		let leftLowerBound = Math.max(minLeft, pairTotalWidth - maxRight);
		let leftUpperBound = Math.min(maxLeft, pairTotalWidth - minRight);
		if (leftLowerBound > leftUpperBound) {
			// If constraints contradict, collapse to nearest feasible value
			leftUpperBound = leftLowerBound;
		}
		// Compute left pane candidate width from absolute pointer position
        const leftCandidate = event.clientX - panesSettings.get(leftId)!.left;
        // Clamp left within derived bounds
        setPanesSettings(leftId, {width: Math.max(leftLowerBound, Math.min(leftCandidate, leftUpperBound))});
        // Right width is whatever remains from the pair total (no resizer width involved here)
        setPanesSettings(rightId, {width: pairTotalWidth - panesSettings.get(leftId)!.width});
	};
</script>

<svelte:window
	onpointermove={(event) => {
		for (const pane of panesSettings.values()) {
			if (pane.resizerActive) {
				resizePanes(event, pane.paneIndex);
			}
		}
	}}
	onpointerup={() => {
		const keys = panesSettings.keys();
        keys.forEach((key) =>  setPanesSettings(key, {resizerActive: false}));
	}}
/>

{#snippet resizer(paneId: string)}
	<div
		class="resizer bg-base-200 flex h-full w-3 cursor-col-resize items-center justify-center"
		role="button"
		aria-label="Resizing panes"
		tabindex="0"
		onpointerdown={() => activateResizer(paneId)}
	>
		<div
			class="resizer-handle {panesSettings.get(paneId)?.resizerActive
				? 'bg-outline'
				: 'bg-outline-variant'} h-20 w-1 rounded-full"
		></div>
	</div>
{/snippet}

<div class="bg-base-200 mt-10 flex flex-col rounded-2xl">
	<div class="flex h-screen w-full p-4">
		{#each panesData as pane, i (pane.id)}
			<div
				class="bg-base-250 grow overflow-y-scroll rounded-xl"
				bind:this={
					() => paneElements.get(pane.id),
					(element) => {
						paneElements.set(pane.id, element);
					}
				}
				bind:clientWidth={
					null,
					(clientWidth) => { typeof clientWidth === 'number' && setPanesSettings(pane.id, {width: clientWidth});
					}
				}
				style:width={(panesSettings.get(pane.id)?.width ?? 300) + 'px'}
			>
				{#if closePane}
					<div class="flex justify-end">
						<button
							class=" btn btn-text btn-sm btn-circle"
							aria-label="Close Button"
							onclick={() => {closePane(pane.id);}}
						>
							<span class="icon-[tabler--x] size-5"></span>
						</button>
					</div>
				{/if}
				<!-- Debugging inforamtion of pane: -->
				<div class="label-small flex flex-col">
					<div class="label">Left: {panesSettings.get(pane.id)?.left} px</div>
					<div class="label">Width: {panesSettings.get(pane.id)?.width} px</div>
					<div class="label">MinWidth: {pane.minWidth} px</div>
					<div class="label">MaxWidth: {pane.maxWidth} px</div>
					<div class="label">
						ResizerActive: {panesSettings.get(pane.id)?.resizerActive ? 'true' : 'false'}
					</div>
				</div>
				{@render pane.content?.()}
			</div>

			{#if i !== panesData.length - 1}
				{@render resizer(panesData[i + 1].id)}
			{/if}
		{/each}
	</div>
</div>
