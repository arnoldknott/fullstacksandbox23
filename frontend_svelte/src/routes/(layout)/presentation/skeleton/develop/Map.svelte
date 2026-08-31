<script lang="ts">
	import 'leaflet/dist/leaflet.css';

	import type L from 'leaflet';
	import type { RevealApi } from 'reveal.js';
	import { onDestroy, onMount } from 'svelte';

	import { Action } from '$lib/accessHandler';
	import { type SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';
	import { initTooltip } from '$lib/userInterface';

	let {
		revealInstance,
		socketio
	}: { revealInstance: RevealApi | undefined; socketio: SocketIO<MessageExtended> } = $props();

	let map: L.Map | null = $state(null);
	let leafletModule: typeof L | null = $state(null);
	let emojiPickerTooltip: HTMLDivElement | undefined = $state();

	type Place = {
		emoji: string;
		name?: string;
		text?: string;
		coords: L.LatLngLiteral;
		marker: L.Marker | undefined;
	};
	// TBD: transfer into a socketio question:
	// sync with socketio.entities!
	let places: Place[] = $derived.by(() => {
		if (socketio?.getSelectedEntities('sortedPlacesAnswers')) {
			return socketio.getSelectedEntities('sortedPlacesAnswers').map((entity) => {
				return JSON.parse(entity.content) as Place;
			});
		} else {
			return [];
		}
	});

	let popupNewPlace: HTMLDivElement | undefined = $state();
	let newPlace: Place | undefined = $state();
	let newPlaceName: string | undefined = $state();
	let newPlaceText: string | undefined = $state();

	$effect(() => {
		if (newPlace) {
			newPlace.name = newPlaceName;
			newPlace.text = newPlaceText;
		}
	});

	// let hideEmojiPicker = $state(true);

	// Wires up emoji selection and keeps the picker's clicks/keystrokes from leaking to
	// FlyonUI's outside-click closer, the Leaflet map, and Reveal's keyboard shortcuts.
	const emojiField = (node: HTMLElement, onselect: (emoji: string) => void) => {
		const swallowed = ['keydown', 'keyup', 'keypress', 'click', 'mousedown', 'dblclick'];
		const stop = (event: Event) => event.stopPropagation();
		const handleSelect = (event: Event) => {
			event.stopPropagation();
			onselect((event as CustomEvent<{ unicode: string }>).detail.unicode);
		};
		swallowed.forEach((type) => node.addEventListener(type, stop));
		node.addEventListener('emoji-click', handleSelect);
		return {
			destroy() {
				swallowed.forEach((type) => node.removeEventListener(type, stop));
				node.removeEventListener('emoji-click', handleSelect);
			}
		};
	};

	$effect(() => {
		if (map && leafletModule) {
			places.forEach((place) => {
				if (!place.marker) {
					// Create marker if it should be shown and doesn't exist

					if (leafletModule && map) {
						// TBD: add {icon: icon } as second argument to marker()
						const emojiIcon = leafletModule?.divIcon({
							html: `<span class="text-4xl">${place.emoji}</span>`,
							className: 'emoji-icon',
							iconAnchor: [14, 32] // Adjust the anchor point to center the icon
						});
						place.marker = leafletModule?.marker(place.coords, { icon: emojiIcon }).addTo(map);
						place.marker?.bindPopup(
							`<div class="bg-secondary-container text-secondary-container-content rounded-lg p-4">
                                <dt class="text-3xl">${place.emoji}<span class="ml-3 ${!place.name ? 'font-normal opacity-60' : ''}">${place.name || 'Anonymous'}</span></dt>
                                ${place.text ? `<dd class="text-2xl ">${place.text}</dd>` : ''}
                            </div>`,
							{ className: 'place-popup' }
						);
					}
					// Remove marker if it shouldn't be shown but exists
					// map?.removeLayer(loc.marker);
					// loc.marker = undefined;
				}
			});
		}
	});

	$effect(() => {
		revealInstance?.on('slidechanged', () => {
			if (map) {
				map.invalidateSize();
			}
		});
	});

	onMount(async () => {
		// Registers the <emoji-picker> custom element.
		await import('emoji-picker-element');
		leafletModule = await import('leaflet');
		// import('leaflet').then((module) => {
		// leafletModule = module;
		map = leafletModule.map('diversityMap', { center: [55.803042, 12.466789], zoom: 3 });

		leafletModule
			.tileLayer(
				'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
				{ attribution: 'Tiles © Esri' }
			)
			.addTo(map);

		map.on('click', (event: L.LeafletMouseEvent) => {
			const { lat, lng } = event.latlng;
			const coords = { lat: lat, lng: lng };
			// Start a fresh place for the popup form to edit.
			newPlace = { emoji: '📍', coords, marker: undefined };
			newPlaceName = undefined;
			newPlaceText = undefined;
			// Add the clicked coordinates to the markers array
			if (map && popupNewPlace) {
				popupNewPlace.classList.remove('hidden');
				leafletModule
					?.popup({
						minWidth: 300,
						className: 'place-popup'
					})
					.setLatLng(event.latlng)
					// .setContent(`You clicked at ${lat.toFixed(4)}, ${lng.toFixed(4)}`)
					.setContent(popupNewPlace)
					.openOn(map);
			}
			// move this to submit Button inside popupNewPlace
			// places = [
			// 	{
			// 		emoji: '📍',
			// 		// coords: { lat: Math.round(lat * 100) / 100, lng: Math.round(lng * 100) / 100 },
			// 		coords,
			// 		marker: undefined
			// 	},
			// 	...places
			// ];
			// });

			// specificIcon = new leafletModule.Icon({
			// 	iconUrl: '{url to specific icon}',
			// 	iconSize: [55, 71],
			// 	iconAnchor: [27, 0],
			// 	popupAnchor: [0, -11]
			// });
		});
	});
	onDestroy(() => {
		map?.remove();
	});
</script>

<div
	bind:this={popupNewPlace}
	class="bg-secondary-container text-secondary-container-content grid hidden w-full grid-cols-6 gap-2 rounded-lg p-4"
>
	<div
		bind:this={emojiPickerTooltip}
		class="tooltip col-span-1 [--interaction:true] [--placement:right-start] [--trigger:click]"
		{@attach initTooltip}
	>
		<div class="tooltip-toggle">
			<button class="btn btn-text w-[40px] text-3xl" aria-label="Emoji Picker"
				>{newPlace?.emoji ?? '📍'}</button
			>
			<!-- svelte-ignore a11y_unknown_role -->
			<div class="tooltip-content tooltip-shown:opacity-100 tooltip-shown:visible" role="popover">
				<div
					class="tooltip-body bg-base-150 shadow-base-shadow max-w-xs rounded-lg p-2 text-start shadow-inner"
				>
					<emoji-picker
						use:emojiField={(emoji) => {
							newPlace = { ...(newPlace as Place), emoji: emoji };
							window.HSTooltip.hide(emojiPickerTooltip);
						}}
					></emoji-picker>
				</div>
			</div>
		</div>
	</div>
	<div class="col-span-5">
		<div class="input-filled input-secondary w-full">
			<input
				type="text"
				placeholder=""
				class="input"
				name="name"
				id="slugInput"
				bind:value={newPlaceName}
			/>
			<label class="input-filled-label" for="slugInput">your name</label>
		</div>
	</div>
	<div class="textarea-filled textarea-base-content col-span-6 w-full">
		<textarea
			class="textarea"
			placeholder="What connects you to this place?"
			id="newPlaceText"
			bind:value={newPlaceText}
			name="text"></textarea>
		<label class="textarea-filled-label" for="newPlaceText">your connection to this place</label>
	</div>
	<div class="col-span-6 text-right">
		<button
			class="btn btn-secondary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
			aria-label="Cancel Button"
			onclick={() => {
				// socketio?.discardEntity(socketio?.pendingEntities[0]);
				map?.closePopup();
			}}
		>
			<span class="icon-[tabler--x] size-4"></span>Cancel
		</button>
		<button
			class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
			aria-label="Submit Button"
			onclick={() => {
				const pending = socketio.pendingEntities[0];
				// Mark the answer public so anonymous participants can create it, and link it to the question.
				socketio.addPendingAccessPolicy(pending.id, {
					public: true,
					action: Action.READ
				});
				pending.content = JSON.stringify(newPlace);
				socketio.submitEntity(pending, socketio.parentId ?? undefined, true);
				socketio.createPending();
				map?.closePopup();
			}}
		>
			<span class="icon-[tabler--send-2] size-5"></span>Send
		</button>
	</div>
</div>

<div class="grid h-full grid-cols-12 grid-rows-[auto_1fr_auto] gap-2">
	<div class="col-span-9 h-fit text-center text-5xl">
		What places do you have a special relation to?
	</div>
	<div class="col-span-3"></div>
	<div class="col-span-9 h-full" id="diversityMap" data-prevent-swipe></div>
	<div class="col-span-3 overflow-y-scroll">
		<div class="mb-3 text-4xl">Click on the map<br /> to add your place</div>

		{#each places as place, index (index)}
			<button
				class="btn btn-soft btn-secondary mb-2 h-fit w-full justify-start p-2 text-left"
				onclick={() => {
					if (place.marker && map) {
						map.flyTo(place.coords, 3);
						place.marker.openPopup();
					}
				}}
			>
				<dl>
					<dt class="text-3xl">
						{place.emoji}
						<span class="ml-1{!place.name ? 'font-normal opacity-60' : ''}"
							>{place.name || 'Anonymous'}</span
						>
					</dt>
					<dd class="text-2xl">{place.text}</dd>
					<!-- {#if index < places.length - 1}
					<div class="divider bg-base-content/20 my-2 h-px"></div>
				{/if} -->
				</dl>
			</button>
		{/each}
	</div>
	<div class="col-span-12 mr-20 text-right text-xl">
		By entering your name and connection to this place, you agree to the <a
			href="#terms-and-conditions"
			class="link link-animated">terms and conditions</a
		>.
	</div>
</div>

<style>
	/* Leaflet builds popup chrome at runtime outside the component's scope, so it must be targeted globally. */
	:global(.leaflet-popup.place-popup .leaflet-popup-content-wrapper) {
		background-color: var(--secondary-container);
		color: var(--secondary-container-content);
		/* box-shadow: none; */
		/* padding: 0;
		border-radius: 0; */
	}
	:global(.leaflet-popup.place-popup .leaflet-popup-content) {
		margin: 0;
		font: inherit;
	}
	:global(.leaflet-popup.place-popup .leaflet-popup-tip) {
		background-color: var(--secondary-container);
		color: var(--secondary-container-content);
	}
	:global(.leaflet-popup.place-popup .leaflet-popup-close-button) {
		font-size: 1.5rem;
		width: 1.75rem;
		height: 1.75rem;
		padding: 0.25rem 0.25rem 0 0;
	}
	:global(emoji-picker) {
		/* --emoji-picker-background-color: var(--base-100);
		--emoji-picker-color: var(--base-content); */
		width: 233px;
		height: 300px;
		--background: var(--base-150);
		--border-size: 0px;
	}
</style>
