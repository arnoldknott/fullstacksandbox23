<script lang="ts" module>
	import type L from 'leaflet';

	export type Place = {
		emoji: string;
		name?: string;
		text?: string;
		coords: L.LatLngLiteral;
		marker?: L.Marker;
	};
</script>

<script lang="ts">
	import 'leaflet/dist/leaflet.css';

	import type { RevealApi } from 'reveal.js';
	import { onDestroy, onMount, type Snippet, tick, untrack } from 'svelte';

	let {
		revealInstance,
		leafletMap = $bindable(),
		places = [],
		popup,
		mobile = false
	}: {
		revealInstance?: RevealApi;
		leafletMap?: L.Map;
		places?: Place[];
		popup?: Snippet<[L.LatLngLiteral, () => void]>;
		mobile?: boolean;
	} = $props();
	let mapElement: HTMLDivElement;
	let popupElement: HTMLDivElement;
	let leafletModule = $state<typeof L>();
	let coordinates = $state<L.LatLngLiteral>();
	let markers: L.Marker[] = [];
	let destroyed = false;

	$effect(() => {
		const currentMap = leafletMap;
		const leaflet = leafletModule;
		const currentPlaces = [...places];
		if (!currentMap || !leaflet) return;
		untrack(() => {
			markers.forEach((marker) => marker.remove());
			markers = currentPlaces.map((place) => {
				const emoji = document.createElement('span');
				emoji.className = mobile ? 'text-2xl' : 'text-4xl';
				emoji.textContent = place.emoji;
				const icon = leaflet.divIcon({
					html: emoji,
					className: 'emoji-icon',
					iconAnchor: [14, 32]
				});
				const marker = leaflet.marker(place.coords, { icon }).addTo(currentMap);
				const content = document.createElement('div');
				content.className =
					'bg-secondary-container text-secondary-container-content rounded-lg p-4';
				const heading = document.createElement('div');
				heading.className = mobile ? 'text-lg' : 'text-3xl';
				heading.textContent = `${place.emoji} ${place.name || 'Anonymous'}`;
				content.append(heading);
				if (place.text) {
					const text = document.createElement('div');
					text.className = mobile ? 'text-base' : 'text-2xl';
					text.textContent = place.text;
					content.append(text);
				}
				marker.bindPopup(content, { className: 'place-popup' });
				place.marker = marker;
				return marker;
			});
		});
	});

	$effect(() => {
		const reveal = revealInstance;
		const invalidate = () => leafletMap?.invalidateSize();
		reveal?.on('slidechanged', invalidate);
		return () => reveal?.off('slidechanged', invalidate);
	});

	$effect(() => {
		if (!leafletMap) return;
		const observer = new ResizeObserver(() => leafletMap?.invalidateSize());
		observer.observe(mapElement);
		return () => observer.disconnect();
	});

	onMount(() => {
		void import('leaflet').then((leaflet) => {
			if (destroyed) return;
			leafletModule = leaflet;
			leafletMap = leaflet.map(mapElement, { center: [55.803042, 12.466789], zoom: 5 });
			leaflet
				.tileLayer(
					'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
					{ attribution: 'Tiles © Esri' }
				)
				.addTo(leafletMap);
			leafletMap.on('click', async (event: L.LeafletMouseEvent) => {
				if (!popup || !leafletMap) return;
				coordinates = { lat: event.latlng.lat, lng: event.latlng.lng };
				await tick();
				if (destroyed || !leafletMap) return;
				leaflet
					.popup({
						minWidth: mobile ? Math.min(300, Math.max(180, mapElement.clientWidth - 48)) : 350,
						maxWidth: mobile ? Math.max(200, mapElement.clientWidth - 48) : 500,
						className: 'place-popup'
					})
					.setLatLng(event.latlng)
					.setContent(popupElement)
					.openOn(leafletMap);
			});
		});
	});

	onDestroy(() => {
		destroyed = true;
		leafletMap?.remove();
		leafletMap = undefined;
	});
</script>

<div class="h-full min-h-0 w-full" bind:this={mapElement} data-prevent-swipe></div>
<div class="hidden">
	<div bind:this={popupElement}>
		{#if coordinates && popup}
			{@render popup(coordinates, () => leafletMap?.closePopup())}
		{/if}
	</div>
</div>

<style>
	/* Leaflet builds popup chrome outside the component's scope. */
	:global(.leaflet-popup.place-popup .leaflet-popup-content-wrapper),
	:global(.leaflet-popup.place-popup .leaflet-popup-tip) {
		background-color: var(--secondary-container);
		color: var(--secondary-container-content);
	}
	:global(.leaflet-popup.place-popup .leaflet-popup-content) {
		margin: 0;
		font: inherit;
	}
	:global(.leaflet-popup.place-popup .leaflet-popup-close-button) {
		font-size: 1.5rem;
		width: 1.75rem;
		height: 1.75rem;
		padding: 0.25rem 0.25rem 0 0;
	}
</style>
