<script lang="ts">
	import type { PageData } from './$types';
	import Heading from '$components/Heading.svelte';
	import { resolve } from '$app/paths';
	import { onDestroy } from 'svelte';

	let { data }: { data: PageData } = $props();
	// TBD refactor using sessionData
	const account = data.account;
	const userProfile = data.userProfile;
	//  This is the raw data fo the file - try demonstrating with a text file or md-file!
	let userPictureBlob = $derived(new Blob([data.userPicture], { type: 'image/jpeg' }));

	let userPictureURL = $state<string | undefined>(undefined);
	$effect(() => {
		if (!userPictureURL) {
			userPictureURL = URL.createObjectURL(userPictureBlob);
		}
	});

	onDestroy(() => userPictureURL && URL.revokeObjectURL(userPictureURL));

	// let userPictureURL: string | undefined = $state(undefined);
	// onMount(async () => {
	// 	const response = await fetch('/api/v1/user/me/picture', { method: 'GET' });
	// 	if (!response.ok && response.status !== 200) {
	// 		console.log('layout - userPictureURL - response not ok');
	// 	} else {
	// 		const pictureBlob = await response.blob();
	// 		if (pictureBlob.size === 0) {
	// 			console.log('layout - userPictureURL - no User picture available');
	// 		} else {
	// 			userPictureURL = URL.createObjectURL(pictureBlob);
	// 		}
	// 	}
	// });
</script>

<Heading>First: Directly from SvelteAPI (works also without client side JavaScript):</Heading>
<Heading>Second: Passed through server load function and uses client side JavaScript:</Heading>
<!-- TBD: needs a check if user is logged in -> using store data?  -->
<div class="flex flex-row gap-4">
	<p class="body-large w-1/6">
		<img class="rounded-full" src="/api/v1/user/me/picture" alt="you" />
		This picture comes from the specific API endpoint in Svelte which is server side fetching from the
		Microsoft Graph API
	</p>

	<!-- TBD: remove the following one: -->
	{#if userPictureURL}
		<p class="body-large w-1/6">
			<img class="rounded-2xl" src={userPictureURL} alt="you" />
			Whereas this one is transferred from the server load function to the client as binary large object
			and then displayed using client side JavaScript.
		</p>
	{/if}

	<p class="body-large w-1/6">
		<img
			class="mask rounded-full"
			src={resolve('/apiproxies/msgraph') + '?endpoint=/me/photo/$value'}
			alt="you"
		/>
		This picture comes from the generic API endpoint in Svelte which is forwards the fetch to the Microsoft
		Graph API
	</p>
	<div
		class="mask-radial-t-0% flex w-1/6 bg-[url(/apiproxies/msgraph?endpoint=/me/photo/$value)] mask-radial-from-1% bg-cover"
	>
		<p class="body-large m-8 self-end">
			Same generic endpoint, just applying mask to the image and use it as a background image.
		</p>
	</div>
</div>

<Heading>Microsoft User Profile on DTU Tenant</Heading>
<code><pre>{JSON.stringify(userProfile, null, ' ')}</pre></code>

<Heading>Azure Account</Heading>
<code><pre>{JSON.stringify(account, null, ' ')}</pre></code>
