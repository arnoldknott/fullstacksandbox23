<script lang="ts">
	import '../app.css';
	import { setContext } from 'svelte';
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';

	// import InitialScrollspy from './InitialScrollspy.svelte';
	// import type { LayoutData } from './$types';
	// import type { Action } from 'svelte/action';
	// import { Variant, Theming, type ColorConfig } from '$lib/theming';
	// import { themeStore } from '$lib/stores';
	// import { initScrollspy } from '$lib/userInterface';
	// import Loreum from './(layout)/Loreum.svelte';
	// import { scrollY } from 'svelte/reactivity/window';
	// import ReproductionScrollspyDocumentationOnBodyScroll from './ReproductionScrollspyDocumentationOnBodyScroll.svelte';

	let { children }: { children: Snippet } = $props();
	// let { data }: { data: LayoutData } = $props();
	// let { children, data }: { children: Snippet; data: LayoutData } = $props();

	setContext('backendAPIConfiguration', page.data.backendAPIConfiguration);

	// let systemDark = $state(false);
	// let mode: 'light' | 'dark' = $state('dark');
	// const theming = $state(new Theming());
	// let themeConfiguration: ColorConfig = $state({
	// 	sourceColor: data?.session?.currentUser?.user_profile.theme_color || '#941ff4', // <= That's a good color!// '#353c6e' // '#769CDF',
	// 	variant: data?.session?.currentUser?.user_profile.theme_variant || Variant.TONAL_SPOT, // Variant.FIDELITY,//
	// 	contrast: data?.session?.currentUser?.user_profile.contrast || 0.0
	// });
	// const applyTheming: Action = (_node) => {
	// 	systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
	// 	mode = systemDark ? 'dark' : 'light';

	// 	let theme = $derived(theming.applyTheme(themeConfiguration, mode));

	// 	$effect(() => {
	// 		themeStore.set(theme);
	// 	});
	// };
</script>

<!-- Remove from here after debugging scrollspy! Belongs to (layout)-->
<!-- <svelte:body use:applyTheming /> -->

<!-- <InitialScrollspy /> -->
<!-- <ReproductionScrollspyDocumentationOnBodyScroll /> -->

<!-- Simple navigation check -->
<!-- <a href="#belowLoreum">Go below Loreum</a>

<Loreum repetition={50} />

<div id="belowLoreum">
	<h2 class="mt-8 mb-4 text-2xl font-bold">You have arrived below the Loreum</h2>
	</div> -->

{@render children?.()}
