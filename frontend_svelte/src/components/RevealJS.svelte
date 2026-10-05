<script lang="ts" module>
	import type { Attachment } from 'svelte/attachments';
	/** Reveal.js adds `.fragment` and `.fragments` to the `fragmentshown` / `fragmenthidden` events. */
	type FragmentEvent = Event & { fragment?: HTMLElement; fragments?: HTMLElement[] };

	// TBD: move the logic into $lib/userInterface.svelte.ts
	// and import it here, so that it can be reused in other presentations
	/**
	 * Attachment for a Reveal.js fragment (the trigger). While that fragment is
	 * shown the given classes are added to the target element; when it is hidden
	 * they are removed again. The target is resolved from a CSS selector, so no
	 * `bind:this` on the target is required.
	 *
	 * Usage:
	 * ```svelte
	 * <div id="goal" class="transition-all duration-1000">Some Text</div>
	 * <div class="fragment fade-in" {@attach toggleOnFragment(reveal, '#goal', 'text-error', 'mr-100')}>
	 *   Some more Text
	 * </div>
	 * ```
	 */
	export const toggleOnFragment = (
		revealInstance: RevealApi,
		targetElement: HTMLElement | (() => HTMLElement | undefined),
		classes: string,
		invert = false
	): Attachment<HTMLElement> => {
		return (node) => {
			const resolveTarget = () =>
				typeof targetElement === 'function' ? targetElement() : targetElement;
			const show = (event: FragmentEvent) => {
				if (event.fragment === node) resolveTarget()?.classList.add(...classes.split(' '));
			};
			const hide = (event: FragmentEvent) => {
				if (event.fragment === node) resolveTarget()?.classList.remove(...classes.split(' '));
			};

			revealInstance?.on(
				'fragmentshown',
				!invert ? (show as EventListener) : (hide as EventListener)
			);
			revealInstance?.on(
				'fragmenthidden',
				!invert ? (hide as EventListener) : (show as EventListener)
			);

			return () => {
				revealInstance?.off(
					'fragmentshown',
					!invert ? (show as EventListener) : (hide as EventListener)
				);
				revealInstance?.off(
					'fragmenthidden',
					!invert ? (hide as EventListener) : (show as EventListener)
				);
			};
		};
	};
</script>

<script lang="ts">
	import 'reveal.js/reveal.css';
	// TBD: investigate where the color scheme is per default loaded for black,
	// so RevealJS also needs to load black as default?
	// for small screens, the black theme needs to be loaded as default,
	// otherwise the slides will be white whitebackground with black's color theme,
	// that is most of the text is very light color and not readable!
	import 'reveal.js/theme/black.css';

	import type { RevealApi, RevealConfig } from 'reveal.js';
	import Reveal from 'reveal.js';
	import revealThemeBlackHref from 'reveal.js/theme/black.css?url';
	import revealThemeWhiteHref from 'reveal.js/theme/white.css?url';
	import { onMount, type Snippet } from 'svelte';

	export const ssr = false;
	// let { children, keyboard=true }: {  children: Snippet, keyboard: boolean} = $props();
	let {
		children,
		options = {},
		reveal = $bindable()
	}: { children: Snippet; options?: RevealConfig; reveal?: RevealApi } = $props();
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
