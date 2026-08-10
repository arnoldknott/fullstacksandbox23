<script lang="ts">
	import { getContext, type Snippet } from 'svelte';

	import theme from '$lib/stores/theme';
	import { FSSB23_THEME_KEY, type ThemeRuntimeContext, Theming } from '$lib/theming';

	let { children }: { children: Snippet } = $props();

	const themeRuntime = getContext<ThemeRuntimeContext>(FSSB23_THEME_KEY);
	const theming = new Theming();

	$effect(() => {
		theme.set(theming.applyTheme(themeRuntime));
	});
</script>

{@render children?.()}
