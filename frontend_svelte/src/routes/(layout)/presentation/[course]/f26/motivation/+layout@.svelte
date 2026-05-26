<script lang="ts">
	import '/src/app.css';

	import type { Snippet } from 'svelte';
	import { getContext } from 'svelte';

	import { FSSB23_THEME_KEY, type ThemeRuntimeContext, Theming } from '$lib/theming';

	let { children }: { children: Snippet } = $props();

	const themeRuntime = getContext<ThemeRuntimeContext>(FSSB23_THEME_KEY);
	const theming = new Theming();

	$effect(() => {
		theming.applyTheme(themeRuntime);
	});
</script>

<div class="h-screen">
	{@render children?.()}
</div>
