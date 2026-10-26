<script lang="ts">
	import { autoUpdate, computePosition, flip, offset, shift } from '@floating-ui/dom';
	import Icon from '@iconify/svelte';
	import type L from 'leaflet';
	import { onDestroy, onMount } from 'svelte';

	import { Action } from '$lib/accessHandler';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

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
	let emojiPickerButton: HTMLButtonElement;
	let emojiPickerPopover: HTMLDivElement;
	let emojiPickerPositioned = $state(false);
	let stopPositioning: (() => void) | undefined;

	const positionPicker = (event: ToggleEvent) => {
		stopPositioning?.();
		stopPositioning = undefined;
		emojiPickerPositioned = false;
		if (event.newState !== 'open') return;
		let active = true;
		const cleanup = autoUpdate(
			emojiPickerButton,
			emojiPickerPopover,
			() => {
				void computePosition(emojiPickerButton, emojiPickerPopover, {
					placement: 'bottom-start',
					strategy: 'fixed',
					middleware: [offset(8), flip({ padding: 8 }), shift({ padding: 8 })]
				}).then(({ x, y }) => {
					if (!active) return;
					emojiPickerPopover.style.left = `${x}px`;
					emojiPickerPopover.style.top = `${y}px`;
					emojiPickerPositioned = true;
				});
			},
			{ animationFrame: true }
		);
		stopPositioning = () => {
			active = false;
			cleanup();
		};
	};

	onDestroy(() => stopPositioning?.());

	// Picker events must not reach Leaflet or Reveal's keyboard shortcuts.
	const emojiField = (node: HTMLElement) => {
		const swallowed = ['keydown', 'keyup', 'keypress', 'click', 'mousedown', 'dblclick'];
		const stop = (event: Event) => event.stopPropagation();
		const handleSelect = (event: Event) => {
			event.stopPropagation();
			emoji = (event as CustomEvent<{ unicode: string }>).detail.unicode;
			emojiPickerPopover.hidePopover();
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
	<button
		bind:this={emojiPickerButton}
		type="button"
		class="btn btn-primary-container btn-circle shadow-base-shadow mt-1 text-2xl shadow"
		aria-label="Emoji Picker"
		popovertarget={`${inputId}-emoji-picker`}>{emoji}</button
	>
	<div
		id={`${inputId}-emoji-picker`}
		bind:this={emojiPickerPopover}
		popover="auto"
		ontoggle={positionPicker}
		aria-label="Choose an emoji"
		class="bg-base-250 text-base-content shadow-base-shadow fixed inset-auto m-0 max-h-[calc(100dvh-2rem)] w-[249px] max-w-[calc(100dvw-2rem)] rounded-lg border-0 p-2 shadow-lg"
		class:invisible={!emojiPickerPositioned}
	>
		<emoji-picker
			class="flex h-[min(300px,calc(100dvh-3rem))] w-full [--background:var(--color-base-250)] [--border-size:0px]"
			use:emojiField
		></emoji-picker>
	</div>
	<div class="min-w-0"><NameInput bind:name /></div>
	<div class="textarea-filled textarea-base-content col-span-2 w-full">
		<textarea class="textarea" placeholder="" id={inputId} bind:value={text} name="text"></textarea>
		<label class="textarea-filled-label text-sm whitespace-normal" for={inputId}
			>How do you connect to this place?</label
		>
	</div>
	<div class="col-span-2 flex flex-wrap justify-end gap-2">
		<button
			class="btn btn-secondary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
			onclick={onclose}
		>
			<Icon icon="tabler:x" class="z-0! size-4" />Cancel
		</button>
		<button
			class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm"
			disabled={!socketio?.pendingEntities[0] || !parentId}
			onclick={submit}
		>
			<Icon icon="tabler:send" class="z-0! size-4" />Send
		</button>
	</div>
</div>
