<script lang="ts">
	import { type SubmitFunction } from '@sveltejs/kit';
	import { getContext, onMount, setContext, type Snippet } from 'svelte';
	import type { Action } from 'svelte/action';
	import { scrollY } from 'svelte/reactivity/window';
	import { writable } from 'svelte/store';

	import { afterNavigate, goto } from '$app/navigation';
	import { page } from '$app/state';
	import { type ArtificialIntelligenceConfig, Model } from '$lib/artificialIntelligence';
	import { SessionStatus } from '$lib/session';
	import { themeStore } from '$lib/stores';
	import { FSSB23_THEME_KEY, type ThemeRuntimeContext, Theming } from '$lib/theming';

	import type { LayoutData } from './$types';
	import NavBar from './NavBar.svelte';
	import SideBar from './SideBar.svelte';
	import WelcomeModal from './WelcomeModal.svelte';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	// console.log("=== layout - client - data ===")
	// console.log(data)

	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		const currentUrl = new URL(page.url);

		if (debug) {
			currentUrl.searchParams.set('debug', 'true');
		} else {
			currentUrl.searchParams.delete('debug');
		}

		// Only navigate if the search params actually changed
		if (currentUrl.search !== page.url.search) {
			goto(`${currentUrl.pathname}${currentUrl.search}${currentUrl.hash}`, {
				replaceState: true,
				noScroll: true,
				keepFocus: true
			});
		}
	});

	let userUnregistered = $derived(
		!data.session?.loggedIn
			? false
			: data.session?.status === SessionStatus.REGISTERED
				? false
				: true
	);

	// put potenitally in onMount to avoid SSR issues
	let parentUrl = $derived(page.url.searchParams.get('parentURL') || undefined);
	// $effect(() => {
	// 	console.log('=== layout.svelte - parentURL ===');
	// 	console.log(parentUrl);
	// });
	// onMount(() => {
	// 	// if (window.self !== window.top && window.top) {
	// 	console.log('=== layout.svelte - running in iframe - window.top.location.href ===');
	// 	console.log(document.referrer);
	// 	// }
	// });
	// onMount(async () => {
	// 	if (window.self !== window.top && window.top) {
	// 		// console.log('=== layout.svelte - running in iframe ===');
	// 		// console.log(document.referrer);

	// 		const localSessionId = localStorage.getItem('session_id');
	// 		const serverHasSession = data.session?.loggedIn === true;
	// 		// const restoreKey = `restore-attempt:${page.url.pathname}${page.url.search}`;
	// 		// sessionStorage.getItem(restoreKey) === '1';
	// 		// console.log('=== layout.svelte - onMount - localSessionId ===');
	// 		// console.log(localSessionId);
	// 		if (localSessionId && !serverHasSession) {
	// 			// console.log('=== layout - restoring session - localSessionId ===');
	// 			// console.log(localSessionId);
	// 			const formData = new FormData();
	// 			formData.append('sessionId', localSessionId);
	// 			try {
	// 				await fetch('?/restoresession', {
	// 					method: 'POST',
	// 					body: formData
	// 				});
	// 				// Trigger SvelteKit data reload (uses fetch, so your auth header override can be applied)
	// 				await invalidateAll();
	// 				// If session is now present, clear guard and stop.
	// 				if (page.data.session?.loggedIn === true) {
	// 					// sessionStorage.removeItem(restoreKey);
	// 					// console.log('=== layout.svelte - session restored ===');

	// 					return;
	// 				}
	// 				// One-time fallback navigation (no hard reload loop)
	// 				await goto(`${page.url.pathname}${page.url.search}`, {
	// 					replaceState: true,
	// 					invalidateAll: true,
	// 					keepFocus: true,
	// 					noScroll: true
	// 				});
	// 				// if (response.ok) {
	// 				// 	console.log('=== layout.svelte - onMount - session mismatch - reloading to sync session ===');
	// 				// 	// window.location.reload();
	// 				// } else {
	// 				// 	console.error('🔥 🚪 layout.svelte - onMount - session restore failed with status:', response.status);
	// 				// 	localStorage.removeItem('session_id');
	// 				// }
	// 			} catch (err) {
	// 				console.error('🔥 🚪 layout.svelte - onMount - session restore failed');
	// 				console.error(err);
	// 				// Optionally, you could choose to clear the local session ID if the restore fails
	// 				// localStorage.removeItem('session_id');
	// 			}
	// 		}
	// 	}
	// });
	let avatarUrl: string | null = $state(null);

	async function loadAvatar() {
		try {
			const sessionId = localStorage.getItem('session_id');

			const response = await fetch('/apiproxies/msgraph?endpoint=/me/photo/$value', {
				method: 'GET',
				headers: sessionId ? { Authorization: `Bearer ${sessionId}` } : {}
			});

			if (!response.ok) {
				throw new Error(`Avatar request failed: ${response.status}`);
			}

			const blob = await response.blob();
			avatarUrl = URL.createObjectURL(blob);
		} catch (err) {
			console.error('Avatar load failed', err);
			avatarUrl = null;
		}
	}

	onMount(() => {
		loadAvatar();

		return () => {
			if (avatarUrl) URL.revokeObjectURL(avatarUrl);
		};
	});

	let welcomeModal: HTMLDivElement | null = $state(null);

	onMount(() => {
		if (userUnregistered) {
			window.HSOverlay.open(welcomeModal);
		}
	});

	let artificialIntelligenceConfiguration: ArtificialIntelligenceConfig = $state({
		enabled: true,
		model: Model.MODEL1,
		temperature: 0.7
		// max_tokens: 2048
	});

	// let artificialIntelligenceForm = $state<HTMLFormElement | null>(null);

	const themeRuntime = getContext<ThemeRuntimeContext>(FSSB23_THEME_KEY);

	// Keep this component's session payload in sync with the shared root-level theme runtime.
	const theming = $state(new Theming());

	$effect(() => {
		if (data.session?.currentUser?.user_profile) {
			data.session.currentUser.user_profile.theme_color =
				themeRuntime.themeConfiguration.sourceColor;
			data.session.currentUser.user_profile.theme_variant = themeRuntime.themeConfiguration.variant;
			data.session.currentUser.user_profile.contrast = themeRuntime.themeConfiguration.contrast;
		}
	});

	let systemDark = $state(false);

	const applyTheming: Action = (_node) => {
		systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		themeRuntime.mode = systemDark ? 'dark' : 'light';

		let theme = $derived(theming.applyTheme(themeRuntime));

		$effect(() => {
			themeStore.set(theme);
		});
	};

	// const { loggedIn } = page.data.session || false;
	const loggedIn = $derived.by(() => {
		if (page.data && page.data.session && page.data.session.loggedIn === true) {
			return true;
		} else {
			return false;
		}
	});

	// Write theming to database:
	let themeForm = $state<HTMLFormElement | null>(null);

	const saveProfileAccount = async () => {
		if (page.data.session?.loggedIn) {
			themeForm?.requestSubmit();
		}
	};

	const updateProfileAccount: SubmitFunction = async () => {
		// Prevents page from updating/reloading:
		return () => {};
	};

	// TBD: potential useful features to encaspulate the scroll into:
	// onMount, afterNavigate $effect, (beforeNavigate), (onNavigate), Attachment, onscrollend, derived, derived.by(), ...?

	// Reactive context for IntersectionObserver (SSR-safe)
	let intersectionObserver = $state<IntersectionObserver | null>(null);
	const scrollObserverContext = {
		get observer() {
			return intersectionObserver;
		},
		set observer(value: IntersectionObserver | null) {
			intersectionObserver = value;
		},
		activeSection: writable<string | undefined>(undefined),
		visibleSections: writable<Set<string>>(new Set())
	};
	setContext('scrollObserver', scrollObserverContext);

	// Create IntersectionObserver in its own onMount (browser-only API)
	onMount(() => {
		const scrollObserverOptions = {
			// rootMargin: '0px',
			// only trigger when being in upper part 100 ox of screen and at least 30% from the bottom
			rootMargin: '-100px 0px -30% 0px',
			scrollMargin: '0px',
			threshold: [0, 1.0] // Track both entering/exiting and fully visible
		};

		const scrollObserverCallback = (
			entries: IntersectionObserverEntry[],
			_observer: IntersectionObserver
		) => {
			scrollObserverContext.visibleSections.update((visible) => {
				const visibleSections = new Set(visible);
				entries.forEach((entry) => {
					const elementId = entry.target.id;
					if (!elementId) return;

					if (entry.isIntersecting) {
						// Section is visible
						visibleSections.add(elementId);
						// console.log('🖲️ => 🪟 - scroll into window:', elementId);
					} else {
						// Section left viewport
						visibleSections.delete(elementId);
						// console.log('🖲️ => 🚪 - scroll out of window:', elementId);
					}
				});

				// Determine active section: pick first visible (topmost in DOM order)
				if (visibleSections.size > 0) {
					// Get first element from Set (maintains insertion order)
					const firstVisible = Array.from(visibleSections)[0];
					scrollObserverContext.activeSection.set(firstVisible);
				} else {
					// No visible sections - clear active
					scrollObserverContext.activeSection.set(undefined);
				}

				return visibleSections;
			});
		};

		intersectionObserver = new IntersectionObserver(scrollObserverCallback, scrollObserverOptions);

		return () => scrollObserverContext.observer?.disconnect();
	});

	// Handle navigation: clear stores and scroll to hash
	afterNavigate(async (_navigation) => {
		// Clear tracking when navigating between pages
		scrollObserverContext.visibleSections.set(new Set());
		scrollObserverContext.activeSection.set(undefined);

		// Handle hash scrolling after navigation
		const hash = location.hash;
		if (hash) {
			// Small delay to ensure DOM is ready
			setTimeout(() => {
				const targetElement = document.getElementById(hash.substring(1));
				if (targetElement) {
					// Compute the actual scrollY that `scrollIntoView` will land
					// on (target's top aligned with viewport top). Do NOT subtract
					// the header height — native scrollIntoView ignores the fixed
					// header, so subtracting would make the positional flag-clear
					// check miss the landing position and the flag would get stuck.
					const rectTop = targetElement.getBoundingClientRect().top;
					intentionalTargetY = Math.max(0, rectTop + (scrollY.current ?? window.scrollY));
					targetElement.scrollIntoView({ behavior: 'smooth' });
				} else {
					intentionalTargetY = scrollY.current ?? window.scrollY;
				}
				handleIntentionalNavigation();
			}, 100);
		} else {
			// Scroll to top if no hash
			intentionalTargetY = 0;
			window.scrollTo({ top: 0, behavior: 'smooth' });
			handleIntentionalNavigation();
		}
	});

	// Constant once measured — main's padding-top must NOT change when the
	// navbar shows/hides, otherwise document height changes and scrollY gets
	// clamped near the page bottom, which the direction check would then
	// misread as "scrolling up" and re-show the navbar (visible bouncing).
	let navBarBottom: number = $state(0);

	// Hide / show  navbar on scroll down / up
	let header: HTMLElement | null = $state(null);
	let previousScrollY = $state(scrollY.current ?? 0);
	let intentionalNavigationInProgress = $state(false);
	// Target scrollY of the in-progress programmatic smooth scroll. The
	// intentional-navigation flag is cleared as soon as the viewport reaches
	// (or passes) this position (positional, not time-based).
	let intentionalTargetY = $state(0);
	// scrollY at the moment the intentional navigation starts — used to know
	// whether the programmatic scroll is heading up or down so the flag can
	// be cleared once the target is reached or crossed in that direction.
	let intentionalStartY = $state(0);

	// Show navbar and mark navigation as intentional:
	const handleIntentionalNavigation = () => {
		if (header) {
			// Show navbar when browser back/forward is used
			intentionalStartY = scrollY.current ?? 0;
			intentionalNavigationInProgress = true;
			header.classList.add('mt-2');
			header.style.top = '0';
		}
	};

	onMount(() => {
		// console.log('=== onMount - navbar ===');
		document.documentElement.style.setProperty('--header-height', `${header?.offsetHeight}px`);
		navBarBottom = header?.offsetHeight ?? 0;

		return () => {
			// Cleanup
			document.documentElement.style.removeProperty('--header-height');
		};
	});

	const windowResizeHandler = (_event: UIEvent) => {
		document.documentElement.style.setProperty('--header-height', `${header?.offsetHeight}px`);
		navBarBottom = header?.offsetHeight ?? 0;
	};

	const toggleTopNavBar = () => {
		const currentScrollY = scrollY.current ?? 0;

		// Positionally clear the intentional-navigation guard once the
		// programmatic smooth scroll has reached or crossed its target in
		// the direction it was heading. Using "crossed" (not just "within 1
		// px") is essential: scrollIntoView may land a couple of pixels off
		// the computed target, and a user who interrupts the smooth scroll
		// can carry scrollY past the target between scroll events. A simple
		// abs-distance check would then miss the window and the flag would
		// stay stuck — visible as "navbar won't hide after in-page hash nav".
		if (intentionalNavigationInProgress) {
			const goingDown = intentionalTargetY >= intentionalStartY;
			const reached = goingDown
				? currentScrollY >= intentionalTargetY - 1
				: currentScrollY <= intentionalTargetY + 1;
			if (reached) {
				intentionalNavigationInProgress = false;
			}
		}

		// Don't hide navbar during intentional navigation (sidebar clicks, browser back/forward)
		if (!intentionalNavigationInProgress) {
			// console.log('=== toggleTopNavBar ===');
			// see https://www.w3schools.com/howto/howto_js_navbar_hide_scroll.asp
			if (header) {
				if (currentScrollY > previousScrollY) {
					// Scrolling down: hide via `top` (NOT transform). Safari/iOS
					// latches transforms on position:fixed elements until the
					// scroll ends, so a transform-based hide would not animate
					// during the scroll. `top` is treated as layout and repaints
					// during scroll in every browser.
					// Crucially: do NOT touch the main padding-top (navBarBottom)
					// here. Document height must stay constant so scrollY isn't
					// clamped near the page bottom (which would be misread as
					// "scrolling up" and bounce the navbar back into view).
					header.classList.remove('mt-2');
					header.style.top = `-${header.offsetHeight}px`;
				} else {
					// Scrolling up: slide navbar back in.
					header.classList.add('mt-2');
					header.style.top = '0';
				}
			}
			previousScrollY = currentScrollY;
		} else {
			// Keep previousScrollY synced so the first real toggle after the
			// programmatic scroll uses a sensible direction baseline.
			previousScrollY = currentScrollY;
		}
	};
</script>

<svelte:window
	onresize={(event) => windowResizeHandler(event)}
	onscroll={toggleTopNavBar}
	onpopstate={handleIntentionalNavigation}
/>

<svelte:body use:applyTheming />

<header
	bind:this={header}
	class="xs:mx-5 xs:mt-5 fixed z-1 mt-2 w-screen px-2 transition-all duration-300"
>
	<NavBar
		{loggedIn}
		{updateProfileAccount}
		{saveProfileAccount}
		{artificialIntelligenceConfiguration}
		bind:themeForm
		bind:themeMode={themeRuntime.mode}
		bind:themeConfiguration={themeRuntime.themeConfiguration}
		{parentUrl}
	/>
</header>

<main
	class="static w-screen transition-[padding-top] duration-300"
	style="padding-top: {navBarBottom + 4}px;"
>
	<!-- class="border-error h-screen w-screen overflow-x-scroll overflow-y-auto border border-4" -->
	<!-- bind:session={data.session} -->
	<WelcomeModal
		session={data.session}
		bind:artificialIntelligenceConfiguration
		bind:themeConfiguration={themeRuntime.themeConfiguration}
		bind:mode={themeRuntime.mode}
		{updateProfileAccount}
		{saveProfileAccount}
	/>

	<!-- TBD: put sidebar into component -->
	<SideBar {loggedIn} {parentUrl} {debug} {navBarBottom} />
	<div class="xs:mx-5 xs:mt-5 h-screen w-screen bg-transparent px-2">
		<div
			id="scrollspy"
			class="sm:overlay-minified:ps-19 overlay-open:ps-0 space-y-4 pt-2 transition-all duration-300 sm:mx-2 sm:mt-2 sm:ps-66"
		>
			<!-- bind:this={contentArea} -->
			{@render children?.()}
			<!-- NavBarBottom: {navBarBottom}
			<br />
			ContentAreaTop: {contentAreaTop}
			<br />
			ContentAreaOffset: {contentAreaOffset}
			<br />
			locationPageHash: {locationPageAndHash?.page}{locationPageAndHash?.hash} -->
		</div>
	</div>
</main>
