<script lang="ts">
	import type { AppTheme } from '$lib/theming';
	// import { getContext } from 'svelte';
	// import { type AppTheme } from '$lib/theming';
	import { hexFromArgb } from '@material/material-color-utilities';
	import { theme } from '../routes/(layout)/layout.svelte'// TBD: consider moving to $lib/stores?


	let { background, color }: { background: string; color: string} = $props();
	const text = background.replace('--md-sys-color-', '').replaceAll('-', ' ');

    // let themeStore: AppTheme = $state()
    // const unsubscribe = theme.subscribe(value => {
    //     // console.log('themeStore:', value);
    //     themeStore = value;
    // });

        
    // //     // console.log('themeStore:', themeStore[themeStore.currentMode].colors['primary']);
    // // });
    // let colorValue = $state()
    // $effect(() => {
    //     if (themeStore === undefined) return;
    //     let colors = themeStore[themeStore.currentMode].colors
    //     const variable = background.replace('--md-sys-color-', '').replace(/-./g, x => x.toUpperCase()[1]) as keyof typeof colors;
    //     // console.log('variable:', variable);
    //     // console.log('color ', variable, ': ', colors[variable])
    //     colorValue = hexFromArgb(colors[variable])
    //     // colorValue = colors[variable]
    // });

	// let theme: AppTheme = $state(getContext('theme'));
	
	
	// console.log('variable:', variable);
	// $effect(() => {console.log('color ', variable, ': ', colors[variable])});
    // console.log('theme:', $theme);
</script>

<div class="flex h-24 grow p-2" style="background-color: var({background});">
	<p class="text-left text-base md:text-xl" style="color: var({color});">
		{text}
		<br>
        <!-- Works, but laggy, when dragging the colors: -->
        <!-- <code class="text-base">{colorValue}</code> -->
        <!-- <code class="text-base">{hexFromArgb(themestore.[themeStore.currentMode]colors[variable])}</code> -->
	</p>
</div>
