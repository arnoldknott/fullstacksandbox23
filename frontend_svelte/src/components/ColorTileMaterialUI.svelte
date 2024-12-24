<script lang="ts">
	// import { getContext } from 'svelte';
	// import { type AppTheme } from '$lib/theming';
	// import { hexFromArgb } from '@material/material-color-utilities';

	let { background, color }: { background: string; color: string } = $props();
	const text = background.replace('--md-sys-color-', '').replaceAll('-', ' ');
	// let theme: AppTheme = $state(getContext('theme'));
	// let colors = $derived(theme[theme.currentMode].colors)
	// const variable = background.replace('--md-sys-color-', '').replace(/-./g, x => x.toUpperCase()[1]) as keyof typeof colors;
	// console.log('variable:', variable);
	// $effect(() => {console.log('color ', variable, ': ', colors[variable])});
</script>

<div class="flex h-24 grow p-2" style="background-color: var({background});">
	<p class="text-left text-base md:text-xl" style="color: var({color});">
		{text}
		<!-- <br>
        <code class="text-base">{hexFromArgb(colors[variable])}</code> -->
	</p>
</div>
