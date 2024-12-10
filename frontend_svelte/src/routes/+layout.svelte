<!-- <script context="module" lang="ts">
	declare function $effect(fn: () => void | (() => void) | Promise<void>): void;
</script> -->
<script lang="ts">
	import '../app.css';
	// import { onMount } from 'svelte';
	import { setContext } from 'svelte';
	// import type { LayoutData } from './$types';
	import type { Snippet } from 'svelte';
	import { page } from '$app/stores';
	import { afterNavigate } from '$app/navigation';
	// import 'flyonui/flyonui.js';
	// import { HSStaticMethods } from 'flyonui/flyonui.js';
	// import { afterNavigate } from "$app/navigation";
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

	// const initFlyonui = async (_node: HTMLElement) => {
	// 	const {HSStaticMethods} = await import('flyonui/flyonui.js')
	// 	HSStaticMethods.autoInit();
	// }

	const loadHSStaticMethods = async () => {
		const { HSStaticMethods } = await import('flyonui/flyonui.js');
		return HSStaticMethods;
	};

	// works with <svelte:window use:initFlyonui />

	// const initFlyonui = (_node: HTMLElement) => {
	// 	afterNavigate( () => {
	// 		loadHSStaticMethods().then((loadedHSStaticMethods) => {
	// 			// console.log('layout - client - -effect calling - autoInit')
	// 			loadedHSStaticMethods.autoInit();
	// 		})
	// 	})
	// }

	// end works with <svelte:window use:initFlyonui />

	// works:

	$effect(() => {
		afterNavigate(() => {
			loadHSStaticMethods().then((loadedHSStaticMethods) => {
				// console.log('layout - client - -effect calling - autoInit')
				loadedHSStaticMethods.autoInit();
			});
		});
	});

	// end works

	// const foo = () => console.log('foo triggered')

	// const loadHSStaticMethods = async () => {
	// 	const {HSStaticMethods} = await import('flyonui/flyonui.js')
	// 	return HSStaticMethods;
	// }

	// $effect(async () => {
	// 	// console.log('layout - client - $page.data')
	// 	// console.log($page.data)
	// 	const {HStaticMethods} = await import('flyonui/flyonui.js');
	// 	console.log('layout - client - -effect calling - initFlyonui')
	// 	HSStaticMethods.autoInit();
	// })
	// onMount(async () => {
	// 	const {HSStaticMethods} = await import('flyonui/flyonui.js');
	// 	afterNavigate(() => {
	// 	// Runs after navigating between pages
	// 	HSStaticMethods.autoInit();
	// 	});
	// });
</script>

<!-- <svelte:window onload={foo} /> -->
<!-- <svelte:window use:initFlyonui /> -->

<main>
	<!-- {initFlyonui()} -->
	{@render children?.()}
	<!-- <slot /> -->
	<!-- <JsonData data={ data?.body?.loggedIn }/> -->
	<!-- <JsonData data={ data.body }/> -->
</main>
