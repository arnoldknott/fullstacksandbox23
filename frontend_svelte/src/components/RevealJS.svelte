<script lang="ts">
	import 'reveal.js/dist/reveal.css';

	import Reveal, { type Api, type Options } from 'reveal.js';
	import revealThemeBlackHref from 'reveal.js/dist/theme/black.css?url';
	import revealThemeWhiteHref from 'reveal.js/dist/theme/white.css?url';
	import { onMount, type Snippet } from 'svelte';

	export const ssr = false;
	// let { children, keyboard=true }: {  children: Snippet, keyboard: boolean} = $props();
	let {
		children,
		options = {},
		reveal = $bindable()
	}: { children: Snippet; options?: Options; reveal?: Api } = $props();
	const THEME_LINK_ID = 'reveal-theme-link';

	const ensureRevealThemeLink = (): HTMLLinkElement => {
		let link = document.getElementById(THEME_LINK_ID) as HTMLLinkElement | null;

		if (!link) {
			link = document.createElement('link');
			link.id = THEME_LINK_ID;
			link.rel = 'stylesheet';
			document.head.appendChild(link);
		}

		return link;
	};

	const applyRevealTheme = (isDark: boolean): void => {
		const link = ensureRevealThemeLink();
		const stylesheetHref = isDark ? revealThemeBlackHref : revealThemeWhiteHref;

		if (link.href !== stylesheetHref) {
			link.href = stylesheetHref;
		}
	};

	onMount(() => {
		const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
		const handleThemeChange = (event: MediaQueryListEvent) => applyRevealTheme(event.matches);

		applyRevealTheme(mediaQuery.matches);
		mediaQuery.addEventListener('change', handleThemeChange);

		reveal = new Reveal({});
		reveal.initialize({
			// Default options
			embedded: true,
			slideNumber: 'c/t',
			width: 1600,
			height: 900,
			margin: 0.01,
			// Override with external options
			...options
		});
		// reveal.on('fragmentshown', (event) => {
		// 	console.log('=== fragment shown ===');
		// 	console.log(event);
		// });

		return () => {
			mediaQuery.removeEventListener('change', handleThemeChange);
		};
	});
</script>

<div class="reveal">
	<div class="slides">
		{@render children?.()}
	</div>
</div>
