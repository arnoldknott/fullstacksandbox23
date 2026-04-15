<script lang="ts">
	import '/src/app.css';
	import type { LayoutData } from '../$types';
	import { Theming, Variant, type ColorConfig } from '$lib/theming';
	import type { Action } from 'svelte/action';
	import type { Snippet } from 'svelte';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	const theming = $state(new Theming());
	let themeConfiguration: ColorConfig = $state({
		sourceColor: data?.session?.currentUser?.user_profile.theme_color || '#941ff4', // <= That's a good color!// '#353c6e' // '#769CDF',
		variant: data?.session?.currentUser?.user_profile.theme_variant || Variant.TONAL_SPOT, // Variant.FIDELITY,//
		contrast: data?.session?.currentUser?.user_profile.contrast || 0.0
	});
	let systemDark = $state(false);
	let mode: 'light' | 'dark' = $state('dark');
	const applyTheming: Action = (_node) => {
		systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		mode = systemDark ? 'dark' : 'light';
		theming.applyTheme(themeConfiguration, mode);
	};
</script>

<svelte:body use:applyTheming />

<div class="h-screen">
	{@render children?.()}
</div>
