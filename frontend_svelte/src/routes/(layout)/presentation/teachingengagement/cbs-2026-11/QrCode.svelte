<script lang="ts">
	import Icon from '@iconify/svelte';
	import QRCode from 'qrcode';

	import CardOverlay from './CardOverlay.svelte';
	import Notification from './Notification.svelte';

	let {
		url,
		modalHidden = $bindable(true),
		buttonHidden
	}: { url: string; modalHidden: boolean; buttonHidden?: boolean } = $props();

	const qrCodePromise = $derived(QRCode.toDataURL(url));
</script>

{#if !buttonHidden}
	<button
		class="btn btn-info btn-gradient label btn shadow-outline relative z-[1000] mx-4 h-20 w-20 rounded-full shadow-sm"
		aria-label="QR Code"
		onclick={() => (modalHidden = !modalHidden)}
	>
		<Icon icon="bi:qr-code" class="size-8" />
	</button>
{/if}
<div
	class="fixed top-1/2 left-1/2 z-[1000] h-fit w-[600px] -translate-x-1/2 -translate-y-1/2"
	class:hidden={modalHidden}
>
	<CardOverlay
		class="h-full bg-white text-black shadow-none"
		bind:hidden={
			() => modalHidden,
			(hidden) => {
				if (hidden) modalHidden = true;
			}
		}
	>
		{#await qrCodePromise}
			<p>Generating QR code…</p>
		{:then qrCodeDataUrl}
			<img src={qrCodeDataUrl} alt="QR Code for {url}" />
			<Notification>
				<a class="link link-animated text-left" href={url} target="_blank" rel="noopener noreferrer"
					>{url}</a
				>
			</Notification>
		{:catch}
			<p>Unable to generate QR code.</p>
		{/await}
	</CardOverlay>
</div>
