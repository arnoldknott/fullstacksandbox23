<!-- <script context="module" lang="ts">
	declare function $effect(fn: () => void | (() => void) | Promise<void>): void;
</script> -->
<script lang="ts">
	import '../app.css';
	// import { onMount } from 'svelte';
	import { setContext } from 'svelte';
	// import type { LayoutData } from './$types';
	import type { Snippet } from 'svelte';
	import { page } from '$app/state'; // TBD: change page to new import
	import { afterNavigate } from '$app/navigation';
	// import type { Attachment } from 'svelte/attachments';
	// import 'flyonui/flyonui.js';
	// import type { HSStaticMethods } from 'flyonui/flyonui.js';
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
	// console.log('layout - client - page.data')
	// console.log(page.data)
	// setContext('backendAPIConfiguration', data.backendAPIConfiguration);
	// TBD: not working in socketio.ts any more!
	// $effect(() => {
	// 	console.log('layout - client - data.backendAPIConfiguration')
	// 	console.log(data.backendAPIConfiguration)
	// 	setContext('backendAPIConfiguration', data.backendAPIConfiguration);
	// })

	// This is causing an error on server side:
	// 	Error: Cannot subscribe to 'page' store on the server outside of a Svelte component, as it is bound to the current request via component context. This prevents state from leaking between users.For more information, see https://svelte.dev/docs/kit/state-management#avoid-shared-state-on-the-server
	//      at get_store (/app/node_modules/@sveltejs/kit/src/runtime/app/stores.js:89:9)
	//     at Object.subscribe (/app/node_modules/@sveltejs/kit/src/runtime/app/stores.js:35:37)
	//     at /app/node_modules/svelte/src/store/utils.js:26:9
	//     at Module.untrack (/app/node_modules/svelte/src/internal/client/runtime.js:854:10)
	//     at Module.subscribe_to_store (/app/node_modules/svelte/src/store/utils.js:25:16)
	//     at Module.store_get (/app/node_modules/svelte/src/internal/server/index.js:351:16)
	//     at _layout (/app/src/routes/+layout.svelte:42:38)
	//     at Root (/app/.svelte-kit/generated/root.svelte:66:3)
	//     at Module.render (/app/node_modules/svelte/src/internal/server/index.js:117:2)
	//     at Function._render [as render] (/app/node_modules/svelte/src/legacy/legacy-server.js:27:18)
	// so better use the $props with page: PageData approach here!
	setContext('backendAPIConfiguration', page.data.backendAPIConfiguration);

	// const initFlyonui = async (_node: HTMLElement) => {
	// 	const {HSStaticMethods} = await import('flyonui/flyonui.js')
	// 	HSStaticMethods.autoInit();
	// }

	// afterNavigate(() => {
	// 	// Runs after navigating between pages
	// 	// console.log('layout - client - -effect calling - autoInit')
	// 	HSStaticMethods.autoInit();
	// });

	// const loadHSStaticMethods = async () => {
	// 	const { HSStaticMethods } = await import('flyonui/flyonui.js');
	// 	return HSStaticMethods;
	// };

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

	// $effect(() => {
	// 	afterNavigate(() => {
	// 		// HSStaticMethods.autoInit();
	// 		loadHSStaticMethods().then((loadedHSStaticMethods) => {
	// 			// console.log('layout - client - -effect calling - autoInit')
	// 			loadedHSStaticMethods.autoInit();
	// 		});
	// 	});
	// });

	// end works

	// update to FlyonUI 2.1.3:

	afterNavigate(async () => {
		// Runs after navigating between pages
		if (!window.HSStaticMethods) {
			await import('flyonui/flyonui.js');
		}
		window.HSStaticMethods.autoInit();
		// HSStaticMethods.autoInit();
	});

	// prepares for using attachments, introduced in Svelte 5.29:
	// const initFlyonUI: Attachment = () => {
	// 	// await loadHSStaticMethods();
	// 	// hssStaticMethods.autoInit();
	// 	// console.log(element.nodeName)
	// 	console.log('layout - client - initFlyonui - called');
	// 	window.HSStaticMethods.autoInit();

	// 	return () => {
	// 		console.log('layout - client - initFlyonui - return function called');
	// 	};

	// };

	// const foo = () => console.log('foo triggered')

	// const loadHSStaticMethods = async () => {
	// 	const {HSStaticMethods} = await import('flyonui/flyonui.js')
	// 	return HSStaticMethods;
	// }

	// $effect(async () => {
	// 	// console.log('layout - client - page.data')
	// 	// console.log(page.data)
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

<!-- TBD: add toggle switch for light and dark mode -->
<!-- <main {@attach initFlyonUI} class="h-100" > -->
<main class="h-100">
	<!-- {initFlyonui()} -->
	{@render children?.()}
	<!-- <slot /> -->
	<!-- <JsonData data={ data?.body?.loggedIn }/> -->
	<!-- <JsonData data={ data.body }/> -->
</main>
