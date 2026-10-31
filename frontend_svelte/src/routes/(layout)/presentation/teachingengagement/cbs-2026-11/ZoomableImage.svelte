<script lang="ts">
	import 'leaflet/dist/leaflet.css';

	import Icon from '@iconify/svelte';
	import type L from 'leaflet';
	// import { Icon } from 'leaflet';
	import { onMount } from 'svelte';

	let { url }: { url: string } = $props();
	let container: HTMLDivElement;
	let mapElement: HTMLDivElement;
	let leaflet = $state<typeof L>();
	let error = $state<string>();
	let resetView = $state<(() => void) | undefined>();
	let zoomIn = $state<(() => void) | undefined>();
	let zoomOut = $state<(() => void) | undefined>();
	let canZoomIn = $state(false);
	let canZoomOut = $state(false);

	onMount(() => {
		let destroyed = false;
		void import('leaflet')
			.then((module) => {
				if (!destroyed) leaflet = module;
			})
			.catch((cause: unknown) => {
				if (destroyed) return;
				console.error('🔥 ZoomableImage - failed to load image viewer', cause);
				error = 'Unable to load the image viewer.';
			});
		return () => {
			destroyed = true;
		};
	});

	$effect(() => {
		const module = leaflet;
		const imageUrl = url;
		if (!module) return;

		error = undefined;
		let map: L.Map | undefined;
		let fitted = false;
		let bounds: L.LatLngBounds | undefined;
		const image = new Image();
		const fail = () => {
			console.error('🔥 ZoomableImage - failed to load image', imageUrl);
			error = 'Unable to load this image.';
		};
		const resize = () => {
			if (!map || !bounds || !container.clientWidth || !container.clientHeight) return;
			const availableHeight =
				container.clientHeight - parseFloat(getComputedStyle(container).paddingBottom);
			if (availableHeight <= 0) return;
			const scale = Math.min(
				1,
				container.clientWidth / image.naturalWidth,
				availableHeight / image.naturalHeight
			);
			mapElement.style.width = `${image.naturalWidth * scale}px`;
			mapElement.style.height = `${image.naturalHeight * scale}px`;
			const fitView = !fitted || map.getZoom() <= map.getMinZoom();
			map.invalidateSize({ pan: false });
			const fitZoom = map.getBoundsZoom(bounds);
			map.setMinZoom(fitZoom);
			if (fitView) map.fitBounds(bounds, { animate: false });
			fitted = true;
		};
		const observer = new ResizeObserver(resize);
		observer.observe(container);
		image.onerror = fail;
		image.onload = () => {
			bounds = module.latLngBounds([0, 0], [image.naturalHeight, image.naturalWidth]);
			map = module.map(mapElement, {
				crs: module.CRS.Simple,
				minZoom: -10,
				maxZoom: 2,
				zoomSnap: 0,
				zoomDelta: 0.5,
				zoomAnimation: false,
				scrollWheelZoom: true,
				wheelPxPerZoomLevel: 3,
				keyboard: false,
				zoomControl: false,
				attributionControl: false
			});
			module.DomEvent.disableClickPropagation(mapElement);
			module.DomEvent.disableScrollPropagation(mapElement);
			module.imageOverlay(imageUrl, bounds, { alt: 'Zoomable image' }).on('error', fail).addTo(map);
			const currentMap = map;
			const imageBounds = bounds;
			resetView = () => currentMap.fitBounds(imageBounds, { animate: false });
			zoomIn = () => currentMap.zoomIn();
			zoomOut = () => currentMap.zoomOut();
			const updateControls = () => {
				const zoom = currentMap.getZoom();
				canZoomIn = zoom < currentMap.getMaxZoom();
				canZoomOut = zoom > currentMap.getMinZoom();
			};
			currentMap.on('zoomend', updateControls);
			resize();
			updateControls();
		};
		image.src = imageUrl;

		return () => {
			image.onload = null;
			image.onerror = null;
			observer.disconnect();
			resetView = undefined;
			zoomIn = undefined;
			zoomOut = undefined;
			map?.remove();
		};
	});
</script>

<div class="flex h-full min-h-0 w-full items-center justify-center pb-12" bind:this={container}>
	<div
		class="shadow-base-shadow h-fit w-fit self-center overflow-hidden rounded-4xl shadow-lg"
		bind:this={mapElement}
		data-prevent-swipe
	>
		{#if resetView}
			<div class="absolute top-3 left-3 z-[1000] flex flex-col gap-1">
				<div class="join join-vertical inline-flex flex-col">
					<button
						type="button"
						class="btn btn-secondary-container btn-outline shadow-base-shadow join-item h-10 w-10 rounded-none rounded-t-full p-0 text-2xl shadow"
						aria-label="Zoom in"
						title="Zoom in"
						disabled={!canZoomIn}
						onclick={zoomIn}><Icon icon="bx:zoom-in" class="text-2xl" /></button
					>
					<button
						type="button"
						class="btn btn-secondary-container btn-outline shadow-base-shadow join-item h-10 w-10 rounded-none rounded-b-full p-0 text-2xl shadow"
						aria-label="Zoom out"
						title="Zoom out"
						disabled={!canZoomOut}
						onclick={zoomOut}><Icon icon="bx:zoom-out" class="text-2xl" /></button
					>
				</div>
				<button
					type="button"
					class="btn btn-secondary-container btn-outline shadow-base-shadow btn-round h-10 w-10 rounded-full p-0 text-2xl shadow"
					aria-label="Reset view"
					title="Reset view"
					onclick={resetView}><Icon icon="bx:reset" class="text-2xl" /></button
				>
			</div>
		{/if}
	</div>
	{#if error}
		<div role="alert" class="text-error">{error}</div>
	{/if}
</div>

<style>
	/* Reveal's image limits otherwise shrink Leaflet's positioned overlay. */
	:global(.reveal .leaflet-image-layer) {
		max-width: none;
		max-height: none;
		margin: 0;
	}
</style>
