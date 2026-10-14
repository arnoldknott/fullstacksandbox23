<script lang="ts">
	import { page } from '$app/state';

	import { getInputsUrl } from '../inputs';
	import QrCode from '../QrCode.svelte';

	let input = $derived(page.url.searchParams.get('input'));
	let qrCodeUrl = $derived(getInputsUrl(page.url, input));
</script>

<QrCode url={qrCodeUrl} modalHidden={false} buttonHidden={true} />
