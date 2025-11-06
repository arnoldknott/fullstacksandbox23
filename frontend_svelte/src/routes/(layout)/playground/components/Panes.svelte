<script lang="ts">
	// import JsonData from '$components/JsonData.svelte';
	import { type Snippet } from 'svelte';
	import { SvelteMap } from 'svelte/reactivity';
	export type PaneData = {
		id: string;
		content: Snippet;
		minWidth?: number;
		maxWidth?: number;
	};
	// export type PaneAPI = {
	// 	closePane: (paneIndex: string) => void;
	// };
	let { panesData, closePane }: { panesData: PaneData[]; closePane?: (paneId: string) => void } =
		$props();

	// Unified runtime pane state merged with incoming PaneData
	type Pane = {
		paneIndex: number;
		// paneElement: HTMLDivElement | null;
		left: number;
		width: number;
		resizerElement?: HTMLDivElement | null;
		resizerActive?: boolean;
	};
	// let panes: SvelteMap<string, Pane> = $derived.by(() =>
	// {
	//     const panesMap = new SvelteMap<string, Pane>()
	//     panesData.forEach((paneData, index) => {
	//         panesMap.set(
	//             paneData.id,
	//             {
	//                 paneIndex: index,
	//                 paneElement: null,
	//                 left: NaN,
	//                 width: 300,
	//                 resizerElement: null,
	//                 resizerActive: false,
	//             }
	//         )
	//     })
	//     return panesMap
	// }
	// )

	let panes: SvelteMap<string, Pane> = new SvelteMap<string, Pane>();

	let paneElements: SvelteMap<string, HTMLDivElement> = new SvelteMap<string, HTMLDivElement>();

	$effect(() => {
		panesData.forEach((paneData, index) => {
			panes.set(paneData.id, {
				paneIndex: index,
				// paneElement: null,
				left: NaN,
				width: 300,
				resizerElement: null,
				resizerActive: false
			});
		});
	});

	// $effect(() =>
	//     panesData.forEach((paneData) => {
	//         panes.set(
	//             paneData.id,
	//             {paneElement: null,
	//             left: NaN,
	//             width: 300,
	//             resizerElement: null,
	//             resizerActive: false,}
	//         )
	//     }
	// )
	// )

	// let panes: Pane[] = $derived(
	//     panesData.map((pd) => ({
	//         ...pd,
	//         paneElement: null,
	//         left: NaN,
	//         width: 300,
	//         resizerElement: null,
	//         resizerActive: false,
	//     }))
	// );

	// $effect(() => {
	//     const previous = $state.snapshot(panes);
	// 	// panes = previous.filter((pane) => panesData.some((pd) => pd.id === pane.id))
	// });

	// const activateResizer = (paneIndex: number) => {
	const activateResizer = (paneId: string) => {
		panes.set(paneId, {
			...panes.get(paneId)!,
			resizerActive: true
		});
	};

	// const resizePanes = (event: PointerEvent, rightResizingPaneId: string) => {
	const resizePanes = (event: PointerEvent, rightResizingPaneIndex: number) => {
		// console.log('Resizing panes at index:', rightResizingPaneIndex);
		// finding the panes involved:
		// const leftPane = panes[rightResizingPaneIndex - 1];
		// const rightPane = panes[rightResizingPaneIndex];
		const keyValues = panes.entries();
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
		const leftPane = panes.get(leftId)!;
		const rightPane = panes.get(rightId)!;
		const leftPaneData = panesData[rightResizingPaneIndex - 1];
		const rightPaneData = panesData[rightResizingPaneIndex];

		// update left in inforamtion in both panes (needs initialization)
		// leftPane.left = leftPane.paneElement?.getBoundingClientRect().left ?? 0;
		// rightPane.left = rightPane.paneElement?.getBoundingClientRect().left ?? 0;
		// panes.set(leftId, {
		//     ...leftPane,
		//     left: leftPane.paneElement?.getBoundingClientRect().left ?? 0,
		// })
		// panes.set(rightId, {
		//     ...rightPane,
		//     left: rightPane.paneElement?.getBoundingClientRect().left ?? 0,
		// })
		const leftPaneElement = paneElements.get(leftId);
		const rightPaneElement = paneElements.get(rightId);
		panes.set(leftId, {
			...leftPane,
			left: leftPaneElement?.getBoundingClientRect().left ?? 0
		});
		panes.set(rightId, {
			...rightPane,
			left: rightPaneElement?.getBoundingClientRect().left ?? 0
		});
		leftPane.left = leftPaneElement?.getBoundingClientRect().left ?? 0;
		rightPane.left = rightPaneElement?.getBoundingClientRect().left ?? 0;
		// Keep only the two adjacent panes affected by this resizer.
		// Maintain their combined width constant during the drag.
		const pairTotalWidth = leftPane.width + rightPane.width; // capture BEFORE updating either
		// const minLeft = leftPane.minWidth ?? 0;
		// const maxLeft = leftPane.maxWidth ?? Infinity;
		// const minRight = rightPane.minWidth ?? 0;
		// const maxRight = rightPane.maxWidth ?? Infinity;
		const minLeft = leftPaneData.minWidth ?? 0;
		const maxLeft = leftPaneData.maxWidth ?? Infinity;
		const minRight = rightPaneData.minWidth ?? 0;
		const maxRight = rightPaneData.maxWidth ?? Infinity;
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
		// // Clamp left within derived bounds
		// leftPane.width = Math.max(leftLowerBound, Math.min(leftCandidate, leftUpperBound));
		// // Right width is whatever remains from the pair total (no resizer width involved here)
		// rightPane.width = pairTotalWidth - leftPane.width;
		// if (isNaN(setLeftWidth) || isNaN(setRightWidth)) {
		//     console.log('""" Computed NaN widths, skipping update ===');
		//     return;
		// }
		// Clamp left within derived bounds
		panes.set(leftId, {
			...panes.get(leftId)!,
			width: Math.max(leftLowerBound, Math.min(leftCandidate, leftUpperBound))
		});
		// Right width is whatever remains from the pair total (no resizer width involved here)
		panes.set(rightId, {
			...panes.get(rightId)!,
			width: pairTotalWidth - panes.get(leftId)!.width
		});
	};
</script>

<svelte:window
	onpointermove={(event) => {
		for (const pane of panes.values()) {
			if (pane.resizerActive) {
				resizePanes(event, pane.paneIndex);
			}
		}
		// if (panes.some((pane) => pane.resizerActive)) {
		// 	resizePanes(
		// 		event,
		// 		panes.findIndex((pane) => pane.resizerActive)
		// 	);
		// }
	}}
	onpointerup={() => {
		// panes.forEach((pane) => (pane.resizerActive = false))
		// panes.values().forEach((pane) => {
		//     panes.set(pane.id, {
		//         ...pane,
		//         resizerActive: false,
		//     })
		// });
		const keyValues = panes.entries();
		for (const [key, pane] of keyValues) {
			panes.set(key, {
				...pane,
				resizerActive: false
			});
		}
	}}
/>

<!-- {#snippet resizer(paneIndex: number)} -->
{#snippet resizer(paneId: string)}
	<div
		class="resizer bg-base-200 flex h-full w-3 cursor-col-resize items-center justify-center"
		role="button"
		aria-label="Resizing panes"
		tabindex="0"
		onpointerdown={() => activateResizer(paneId)}
	>
		<!-- onpointerdown={() => activateResizer(paneIndex)} -->
		<!-- bind:this={resizerElement} -->
		<!-- bind:this={panes[paneIndex].resizerElement} -->
		<!-- <div
			class="resizer-handle {panes[paneIndex].resizerActive
				? 'bg-outline'
				: 'bg-outline-variant'} h-20 w-1 rounded-full"
		></div> -->
		<div
			class="resizer-handle {panes.get(paneId)?.resizerActive
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
					(clientWidth) => {
                        panes.set(pane.id, {
                            ...panes.get(pane.id),
                            width: clientWidth
                        } as Pane);
					}
				}
				style:width={(panes.get(pane.id)?.width ?? 300) + 'px'}
			>
				{#if closePane}
					<div class="flex justify-end">
						<button
							class=" btn btn-text btn-sm btn-circle"
							aria-label="Close Button"
							onclick={() => {
								// panes = panes.filter((p) => p.id !== pane.id);
								closePane(pane.id);
							}}
						>
							<span class="icon-[tabler--x] size-5"></span>
						</button>
					</div>
				{/if}
				<!-- Degugging inforamtion of pane: -->
				<div class="label-small flex flex-col">
					<!-- <div class="label">Left: {pane.left} px</div>
					<div class="label">Width: {pane.width} px</div>-->
					<div class="label">Left: {panes.get(pane.id)?.left} px</div>
					<div class="label">Width: {panes.get(pane.id)?.width} px</div>
					<div class="label">MinWidth: {pane.minWidth} px</div>
					<div class="label">MaxWidth: {pane.maxWidth} px</div>
					<!-- <div class="label">ResizerActive: {pane.resizerActive ? 'true' : 'false'}</div> -->
					<div class="label">
						ResizerActive: {panes.get(pane.id)?.resizerActive ? 'true' : 'false'}
					</div>
				</div>
				{@render pane.content?.()}
			</div>

			{#if i !== panesData.length - 1}
				<!-- {@render resizer(i + 1)} -->
				<!-- {@render resizer(panes.get(pane.id)!.paneIndex + 1)} -->
				{@render resizer(panesData[i + 1].id)}
			{/if}
		{/each}
	</div>
</div>
