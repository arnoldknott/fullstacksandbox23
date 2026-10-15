<script lang="ts">
	import type L from 'leaflet';
	import type { RevealApi } from 'reveal.js';

	import type { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

	import Map, { type Place } from './Map.svelte';
	import PlaceForm from './PlaceForm.svelte';

	let {
		revealInstance,
		socketio
	}: { revealInstance?: RevealApi; socketio?: SocketIO<MessageExtended> } = $props();
	let leafletMap = $state<L.Map>();
	let name = $state('');
	let places: Place[] = $derived(
		(socketio?.getSelectedEntities('sortedPlacesAnswers') ?? []).flatMap((entity) => {
			try {
				const place = JSON.parse(entity.content) as Place;
				return place?.coords ? [{ ...place, name: entity.confidential || 'Anonymous' }] : [];
			} catch {
				return [];
			}
		})
	);
</script>

<div class="grid h-full grid-cols-12 grid-rows-[auto_1fr_auto] gap-2">
	<div class="col-span-9 h-fit text-center text-5xl">
		What places do you have a special relation to?
	</div>
	<div class="col-span-3 h-fit text-center text-5xl"></div>
	<div class="col-span-9 h-full min-h-0">
		<Map {revealInstance} {places} bind:leafletMap>
			{#snippet popup(coords, close)}
				{#key coords}
					<PlaceForm
						{socketio}
						parentId={socketio?.parentId ?? undefined}
						{coords}
						bind:name
						onclose={close}
					/>
				{/key}
			{/snippet}
		</Map>
	</div>
	<div class="col-span-3 overflow-y-scroll">
		<div class="mb-3 text-4xl">Click on the map<br /> to add your place</div>
		{#each places as place, index (index)}
			<button
				class="btn btn-soft btn-secondary mb-2 h-fit w-full justify-start p-2 text-left"
				onclick={() => {
					leafletMap?.flyTo(place.coords, 3);
					place.marker?.openPopup();
				}}
			>
				<dl>
					<dt class="text-3xl">
						{place.emoji}<span class="ml-1">{place.name || 'Anonymous'}</span>
					</dt>
					<dd class="text-2xl">{place.text}</dd>
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
