<script lang="ts">
	import Icon from '@iconify/svelte';
	import type L from 'leaflet';
	import { onMount } from 'svelte';

	import { Action } from '$lib/accessHandler';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';
	import { initTooltip } from '$lib/userInterface';

	import type { Place } from './Map.svelte';
	import NameInput from './NameInput.svelte';

	let {
		socketio,
		parentId,
		coords,
		name = $bindable(''),
		onclose,
		onsubmit
	}: {
		socketio?: SocketIO<MessageExtended>;
		parentId?: string;
		coords: L.LatLngLiteral;
		name?: string;
		onclose: () => void;
		onsubmit?: (place: Place) => void;
	} = $props();
	const inputId = $props.id();
	let emoji = $state('📍');
	let text = $state('');
	let emojiPickerTooltip: HTMLDivElement;

	// Picker events must not reach Leaflet, Reveal, or FlyonUI's outside-click closer.
	const emojiField = (node: HTMLElement) => {
		const swallowed = ['keydown', 'keyup', 'keypress', 'click', 'mousedown', 'dblclick'];
		const stop = (event: Event) => event.stopPropagation();
		const handleSelect = (event: Event) => {
			event.stopPropagation();
			emoji = (event as CustomEvent<{ unicode: string }>).detail.unicode;
			window.HSTooltip.hide(emojiPickerTooltip);
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
	onMount(() => {
		void import('emoji-picker-element');
	});

	const submit = () => {
		const pending = socketio?.pendingEntities[0];
		if (!socketio || !pending || !parentId) return;
		const place = { emoji, text, coords };
		pending.content = JSON.stringify(place);
		pending.confidential = name.trim() || 'Anonymous';
		socketio.addPendingAccessPolicy(pending.id, { public: true, action: Action.READ });
		socketio.submitEntity(pending, parentId, true);
		socketio.createPending();
		onsubmit?.({ ...place, name: pending.confidential });
		onclose();
	};
</script>

<div
	class="bg-secondary-container text-secondary-container-content grid w-full min-w-61 grid-cols-[2.5rem_minmax(0,1fr)] gap-2 rounded-lg p-4 pr-8"
>
	<div
		bind:this={emojiPickerTooltip}
		class="tooltip [--interaction:true] [--placement:right-start] [--trigger:click]"
		{@attach initTooltip}
	>
		<div class="tooltip-toggle">
			<button
				class="btn btn-secondary btn-circle shadow-base-shadow mt-1 text-2xl shadow"
				aria-label="Emoji Picker">{emoji}</button
			>
			<div class="tooltip-content tooltip-shown:visible tooltip-shown:opacity-100">
				<div
					class="tooltip-body bg-base-150 shadow-base-shadow max-w-xs rounded-lg p-2 text-start shadow-inner"
				>
					<emoji-picker use:emojiField></emoji-picker>
				</div>
			</div>
		</div>
	</div>
	<div class="min-w-0"><NameInput bind:name /></div>
	<div class="textarea-filled textarea-base-content col-span-2 w-full">
		<textarea class="textarea" placeholder="" id={inputId} bind:value={text} name="text"></textarea>
		<label class="textarea-filled-label text-sm whitespace-normal" for={inputId}
			>What connects you to this place?</label
		>
	</div>
	<div class="col-span-2 flex flex-wrap justify-end gap-2">
		<button
			class="btn btn-secondary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
			onclick={onclose}
		>
			<Icon icon="tabler:x" class="size-4" />Cancel
		</button>
		<button
			class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
			disabled={!socketio?.pendingEntities[0] || !parentId}
			onclick={submit}
		>
			<Icon icon="tabler:send" class="size-5" />Send
		</button>
	</div>
</div>

<style>
	:global(emoji-picker) {
		width: 233px;
		height: 300px;
		--background: var(--base-150);
		--border-size: 0px;
	}
</style>
