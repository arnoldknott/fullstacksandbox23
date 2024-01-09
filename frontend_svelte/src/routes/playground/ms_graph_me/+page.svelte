<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageData } from './$types';
	

	let userPictureURL: URL = undefined;
	onMount( async () => {
		const response = await fetch('/api/v1/user/me/picture', {method: 'GET'});
		if (!response.ok && response.status !== 200) {
		} else {
			const pictureBlob = await response.blob()
			if (pictureBlob.size === 0) {
			} else {
				userPictureURL = URL.createObjectURL(pictureBlob);
			}
		}}
	)

	export let data: PageData;
</script>

<code><pre>{JSON.stringify(data.body, null, ' ')}</pre></code>

<p >
	Directly from API - works also without client side JavaScript:
	
	<!-- TBD: needs a check if user is logged in -> using store data?  -->
	<img class="rounded-full" src="/api/v1/user/me/picture" alt="you" />
	</p>

<p>
From fetch:
{#if userPictureURL}
	<img class="h-100 w-100" src={userPictureURL} alt="you" />
{/if}
</p>


