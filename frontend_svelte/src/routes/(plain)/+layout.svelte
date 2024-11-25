<script lang="ts">
	import '../../app.css';
	// import { onMount } from 'svelte';
	import { user_store } from '$lib/stores';
	import { setContext } from 'svelte';
	import type { LayoutData } from '../$types';
	import type { Snippet } from 'svelte';
	// import JsonData from '$components/JsonData.svelte';
	// import Guard from '$components/Guard.svelte';
	// import type { User } from 'src/types.d.ts';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();
	// let data: LayoutData = $props();
	// console.log('layout - client - data')
	// console.log(data)

	// gather these three in one session object
	// $: userProfile = data?.body?.userProfile;
	// $: userAgent = data?.body?.userAgent;
	// $: loggedIn = data?.body?.loggedIn || false;
	const session = data?.body?.sessionData;
	const loggedIn = session?.loggedIn || false;

	if (loggedIn) {
		user_store.set(session);
	}

	setContext('backendAPIConfiguration', data?.body?.backendAPIConfiguration);

	// console.log('layout - client - userProfile')
	// console.log(userProfile)

	// console.log('layout - client - data')
	// console.log(data)
	// console.log('layout - client - $page.data')
	// console.log($page.data)

	// TBD use $page.data for that - that's the standard store, and user logged in information is relevant everywhere.
	// if ($user_store?.loggedIn) {
	// 	user_store.set(data.user);
	// }

	// let userPictureURL: URL | undefined = $state(undefined);
	// onMount(async () => {
	// 	const response = await fetch('/api/v1/user/me/picture', { method: 'GET' });
	// 	if (!response.ok && response.status !== 200) {
	// 		console.log('layout - userPictureURL - response not ok');
	// 		console.log(response);
	// 	} else {
	// 		const pictureBlob = await response.blob();
	// 		if (pictureBlob.size === 0) {
	// 			console.log('layout - userPictureURL - no User picture available');
	// 			console.log(pictureBlob);
	// 		} else {
	// 			userPictureURL = URL.createObjectURL(pictureBlob);
	// 		}
	// 	}
	// });

	// if (data?.loggedIn) {
	// 	$user_store = data;
	// }
</script>

<main>
	{@render children?.()}
	<!-- <slot /> -->
	<!-- <JsonData data={ data?.body?.loggedIn }/> -->
	<!-- <JsonData data={ data.body }/> -->
</main>
