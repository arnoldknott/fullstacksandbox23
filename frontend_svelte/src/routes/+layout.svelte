<script lang="ts">
	import '../app.css';
	// import { onMount } from 'svelte';
	import { setContext } from 'svelte';
	// import type { LayoutData } from './$types';
	import type { Snippet } from 'svelte';
	import { page } from '$app/stores';
	// import JsonData from '$components/JsonData.svelte';
	// import Guard from '$components/Guard.svelte';
	// import type { User } from 'src/types.d.ts';

	// let { data, children }: { data: LayoutData; children: Snippet } = $props();
	let { children }: { children: Snippet } = $props();
	// let data: LayoutData = $props();
	// console.log('layout - client - data')
	// console.log(data)

	// gather these three in one session object
	// $: userProfile = data?.body?.userProfile;
	// $: userAgent = data?.body?.userAgent;
	// $: loggedIn = data?.body?.loggedIn || false;
	// const session = data?.body?.sessionData;
	// const loggedIn = session?.loggedIn || false;
	// console.log('layout - client - data')
	// console.log(data)
	// console.log('layout - client - $page.data')
	// console.log($page.data)
	// setContext('backendAPIConfiguration', data.backendAPIConfiguration);
	// TBD: not working in socketio.ts any more!
	// $effect(() => {
	// 	console.log('layout - client - data.backendAPIConfiguration')
	// 	console.log(data.backendAPIConfiguration)
	// 	setContext('backendAPIConfiguration', data.backendAPIConfiguration);
	// })
	setContext('backendAPIConfiguration', $page.data.backendAPIConfiguration);
</script>

<main>
	{@render children?.()}
	<!-- <slot /> -->
	<!-- <JsonData data={ data?.body?.loggedIn }/> -->
	<!-- <JsonData data={ data.body }/> -->
</main>
