<script lang="ts">
	import type { LayoutData } from './$types';
	import { SessionStatus } from '$lib/session';
	import { Variant, Theming, type ColorConfig } from '$lib/theming';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
	import type { Action } from 'svelte/action';
	import { onMount, type Snippet } from 'svelte';
	import { page } from '$app/state';
	import Guard from '$components/Guard.svelte';
	import { initDropdown, initOverlay } from '$lib/userInterface';
	import ThemePicker from '../../../components/ThemePicker.svelte';
	import ArtificialIntelligencePicker from '../../../components/ArtificialIntelligencePicker.svelte';
	import { themeStore } from '$lib/stores';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { resolve } from '$app/paths';
	import WelcomeModal from '../../../../WelcomeModal.svelte';
	import { afterNavigate, replaceState, pushState, goto } from '$app/navigation';
	import type { SidebarItemContent, Session } from '$lib/types';
	import SidebarItem from '../../../../SidebarItem.svelte';
	import LoginOutButton from '../../../../LoginOutButton.svelte';
	import Logo from '../../../../Logo.svelte';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		if (debug) {
			goto(`?debug=true`, { replaceState: true });
		} else {
			goto(`?`, { replaceState: true });
		}
	});

	let userUnregistered = $derived(
		!data.session?.loggedIn
			? false
			: data.session?.status === SessionStatus.REGISTERED
				? false
				: true
	);

	let session: Session | undefined = $state(data.session);

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

	let artificialIntelligenceForm = $state<HTMLFormElement | null>(null);

	const theming = $state(new Theming());

	// TBD: refactor this to decently use the reactivity of Svelte - potentially use $derived!
	let themeConfiguration: ColorConfig = $state({
		sourceColor: data?.session?.currentUser?.user_profile.theme_color || '#941ff4', // <= That's a good color!// '#353c6e' // '#769CDF',
		variant: data?.session?.currentUser?.user_profile.theme_variant || Variant.TONAL_SPOT, // Variant.FIDELITY,//
		contrast: data?.session?.currentUser?.user_profile.contrast || 0.0
	});

	$effect(() => {
		if (data.session?.currentUser?.user_profile) {
			data.session.currentUser.user_profile.theme_color = themeConfiguration.sourceColor;
			data.session.currentUser.user_profile.theme_variant = themeConfiguration.variant;
			data.session.currentUser.user_profile.contrast = themeConfiguration.contrast;
		}
	});

	let systemDark = $state(false);
	let mode: 'light' | 'dark' = $state('dark');

	const applyTheming: Action = (_node) => {
		systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		mode = systemDark ? 'dark' : 'light';

		let theme = $derived(theming.applyTheme(themeConfiguration, mode));

		$effect(() => {
			themeStore.set(theme);
		});
	};

	const { loggedIn } = page.data.session || false;

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

	// Sidebar:
	let sidebarLinks: SidebarItemContent[] = $state([
		{
			name: 'Docs',
			pathname: resolve('/(plain)/docs'),
			icon: 'icon-[oui--documentation]',
			id: 'docs',
			items: []
		},
		{
			name: 'Playground',
			pathname: resolve('/(layout)/playground'),
			icon: 'icon-[mdi--playground-seesaw]',
			id: 'playground',
			items: [
				{
					name: 'Overview',
					pathname: resolve('/(layout)/playground') + '#top',
					icon: 'icon-[mdi--playground-seesaw]',
					id: 'overview'
				},
				{
					name: 'User Interface',
					pathname: resolve('/(layout)/playground/user-interface'),
					icon: 'icon-[mdi--monitor-dashboard]',
					id: 'user-interface',
					items: []
				},
				{
					name: 'Components',
					pathname: resolve('/(layout)/playground/components') + '?prod=false&develop=true',
					icon: 'icon-[tabler--components]',
					id: 'components',
					items: []
				},
				{
					name: 'Design',
					pathname: resolve('/(layout)/playground/design'),
					icon: 'icon-[fluent--design-ideas-20-regular]',
					id: 'design',
					items: [
						{
							name: 'Backgrounds',
							icon: 'icon-[mdi--palette-outline]',
							hash: '#backgrounds-and-surfaces',
							id: 'backgrounds'
						},
						{
							name: 'Foregrounds',
							icon: 'icon-[mdi--palette-outline]',
							hash: '#foregrounds',
							id: 'foregrounds'
						},
						{
							name: 'Components',
							icon: 'icon-[mdi--palette-outline]',
							hash: '#components',
							id: 'components'
						},
						{
							name: 'Playground',
							icon: 'icon-[mdi--playground-seesaw]',
							hash: '#design-playground',
							id: 'design-playground'
						},
						{
							name: 'Building Blocks',
							icon: 'icon-[clarity--blocks-group-line]',
							hash: '#design-building-blocks',
							id: 'design-building-blocks',
							items: [
								{
									name: 'FlyonUI',
									icon: 'icon-[mingcute--arrows-up-fill]',
									pathname: resolve('/(layout)/playground/design/flyonui'),
									id: 'flyonui'
								},
								{
									name: 'Material Design',
									icon: 'icon-[mdi--material-design]',
									pathname: resolve('/(layout)/playground/design/materialdesign'),
									id: 'material-design'
								},
								{
									name: 'Svelte',
									icon: 'icon-[tabler--brand-svelte]',
									pathname: resolve('/(layout)/playground/design/svelte'),
									id: 'svelte'
								}
							]
						}
					]
				},
				{
					name: 'Data Flow & Navigation',
					pathname: resolve('/(layout)/playground/dataflow'),
					icon: 'icon-[iconoir--data-transfer-both]',
					id: 'dataflow'
				},
				{
					name: 'Backend Schema',
					pathname: resolve('/(layout)/playground/backend-schema'),
					icon: 'icon-[file-icons--openapi]',
					id: 'backend-schema'
				},
				{
					name: 'Counter',
					pathname: resolve('/(layout)/playground/counter'),
					icon: 'icon-[mdi--counter]',
					id: 'counter'
				},
				{
					name: 'Core',
					pathname: resolve('/(layout)/playground/core'),
					icon: 'icon-[streamline-ultimate--computer-chip-core]',
					id: 'core'
				},
				{
					name: 'Websockets',
					pathname: resolve('/(layout)/playground/websockets'),
					icon: 'icon-[solar--socket-linear]',
					id: 'websockets'
				}
			]
		}
		// {
		// 	name: 'Apps',
		// 	pathname: resolve('/(layout)/(protected)/dashboard'),
		// 	icon: 'icon-[material-symbols--dashboard-outline-rounded]',
		// 	id: 'apps',
		// 	items: []
		// },
	]);

	let protectedSidebarLinks: SidebarItemContent[] = $state([
		{
			name: 'Dashboard',
			pathname: resolve('/(layout)/(protected)/dashboard'),
			icon: 'icon-[material-symbols--dashboard-outline-rounded]',
			id: 'dashboard',
			items: [
				{
					name: 'Overview',
					pathname: resolve('/(layout)/(protected)/dashboard') + '#top',
					icon: 'icon-[material-symbols--dashboard-outline-rounded]',
					id: 'overview'
				},
				{
					name: 'Demo Resources',
					pathname: resolve('/(layout)/(protected)/dashboard/backend-demo-resource'),
					icon: 'icon-[grommet-icons--resources]',
					id: 'demo-resource',
					items: [
						{
							name: 'Rest API',
							pathname: resolve('/(layout)/(protected)/dashboard/backend-demo-resource/restapi'),
							icon: 'icon-[dashicons--rest-api]',
							id: 'demo-resource-restapi'
						},
						{
							name: 'Socket IO',
							pathname: resolve('/(layout)/(protected)/dashboard/backend-demo-resource/socketio'),
							icon: 'icon-[tabler--brand-socket-io]',
							id: 'demo-resource-socketio'
						}
					]
				},
				{
					name: 'Hierarchical Resources',
					pathname: resolve('/(layout)/(protected)/dashboard/backend-protected-hierarchy'),
					icon: 'icon-[fluent-mdl2--family]',
					id: 'hierarchical-resources'
				},
				{
					name: 'Identities',
					// pathname: resolve('/(layout)/(protected)/dashboard/identities'),
					icon: 'icon-[material-symbols--identity-platform-outline-rounded]',
					id: 'identities',
					items: [
						{
							name: 'All identities',
							pathname: resolve('/(layout)/(protected)/dashboard/identities'),
							icon: 'icon-[mdi--account-multiple-outline]',
							id: 'identities-all'
						},
						{
							name: 'Microsoft',
							pathname: resolve('/(layout)/(protected)/dashboard/msgraph'),
							icon: 'icon-[fluent--person-20-filled]',
							id: 'identities-microsoft'
						}
					]
				},
				{
					name: 'Socket.IO',
					pathname: resolve('/(layout)/(protected)/dashboard/socketio'),
					icon: 'icon-[tabler--brand-socket-io]',
					id: 'socketio'
				}
			]
		}
	]);

	let debugSidebarLinks: SidebarItemContent[] = $state([
		{
			name: 'Page 1',
			pathname: resolve('/(layout)/playground/page1'),
			icon: 'icon-[tabler--user]',
			id: 'page1',
			items: []
		},
		{
			name: 'Page 2',
			pathname: resolve('/(layout)/playground/page2'),
			icon: 'icon-[icon-park-outline--page]',
			id: 'page2',
			items: [
				{
					id: 'page2-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#pg2loreum1'
				},
				{
					id: 'page2-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#pg2loreum2'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#pg2sub-category',
					id: 'page2-sub-category',
					items: [
						{
							id: 'page2-loreum3',
							name: 'Loreum 3',
							icon: 'icon-[mdi--text]',
							hash: '#pg2loreum3'
						},
						{
							id: 'page2-loreum4',
							name: 'Loreum 4',
							icon: 'icon-[mdi--text]',
							hash: '#pg2loreum4'
						}
					]
				},
				{
					id: 'page2-loreum5',
					name: 'Loreum 5',
					icon: 'icon-[mdi--text]',
					hash: '#pg2loreum5'
				},
				{
					id: 'page2-loreum6',
					name: 'Loreum 6',
					icon: 'icon-[mdi--text]',
					hash: '#pg2loreum6'
				}
			]
		},
		{
			name: 'Page 3',
			pathname: resolve('/(layout)/playground/page3'),
			icon: 'icon-[icon-park-outline--page]',
			id: 'page3',
			items: [
				{
					id: 'page3-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#pg3loreum1'
				},
				{
					id: 'page3-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#pg3loreum2'
				},
				{
					id: 'page3-loreum2a',
					name: 'Loreum 2a',
					icon: 'icon-[mdi--text]',
					hash: '#pg3loreum2a'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#pg3sub-category',
					id: 'pg3sub-category',
					items: [
						{
							id: 'page3-loreum3p1',
							name: 'Loreum 3.1',
							icon: 'icon-[mdi--text]',
							hash: '#pg3loreum3p1'
						},
						{
							id: 'page3-loreum3p2',
							name: 'Loreum 3.2',
							icon: 'icon-[mdi--text]',
							hash: '#pg3loreum3p2'
						}
					]
				},
				{
					id: 'page3-loreum4',
					name: 'Loreum 4',
					icon: 'icon-[mdi--text]',
					hash: '#pg3loreum4'
				},
				{
					id: 'page3-loreum5',
					name: 'Loreum 5',
					icon: 'icon-[mdi--text]',
					hash: '#pg3loreum5'
				}
			]
		},
		{
			id: 'further-page',
			name: 'Further Page',
			pathname: resolve('/(layout)/playground/page4'),
			icon: 'icon-[tabler--mail]',
			items: [
				{
					id: 'page4-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#loreum1'
				},
				{
					id: 'page4-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#sub-category-page4',
					id: 'page4-sub-category',
					items: [
						{
							id: 'page4-loreum3',
							name: 'Loreum 3',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3'
						},
						{
							id: 'page4-loreum4',
							name: 'Loreum 4',
							icon: 'icon-[mdi--text]',
							hash: '#loreum4'
						}
					]
				},
				{
					id: 'page4-sub-pages-section',
					name: 'Sub-pages',
					icon: 'icon-[mdi--text]',
					hash: '#page4-sub-pages-section'
				},
				{
					name: 'Sub-page 4.1',
					icon: 'icon-[mingcute--directory-line]',
					pathname: resolve('/(layout)/playground/page4/page4-1'),
					id: 'page4p1',
					items: [
						{
							id: 'page4p1-loreum1',
							name: 'Loreum 1 pg4.1',
							icon: 'icon-[mdi--text]',
							pathname: resolve('/(layout)/playground/page4/page4-1'),
							hash: '#loreum1'
						},
						{
							id: 'page4p1-loreum2',
							name: 'Loreum 2 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve('/(layout)/playground/page4/page4-1'),
							hash: '#loreum2'
						}
					]
				},
				{
					name: 'Sub-page 4.2',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					pathname: resolve('/(layout)/playground/page4/page4-2'),
					id: 'page4p2',
					items: [
						{
							id: 'page4p2-loreum1',
							name: 'Loreum 1 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve('/(layout)/playground/page4/page4-2'),
							hash: '#loreum1'
						},
						{
							id: 'page4p2-loreum2',
							name: 'Loreum 2 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve('/(layout)/playground/page4/page4-2'),
							hash: '#loreum2'
						}
					]
				},
				{
					id: 'page4-loreum6',
					name: 'Loreum 6',
					icon: 'icon-[mdi--text]',
					hash: '#loreum6'
				}
			]
		},
		{
			name: 'Page 5',
			pathname: resolve('/(layout)/playground/page5'),
			icon: 'icon-[tabler--user]',
			id: 'page5',
			items: [
				{
					id: 'page5-loreum1',
					name: 'Loreum 1',
					icon: 'icon-[mdi--text]',
					hash: '#loreum1'
				},
				{
					id: 'page5-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2'
				}
			]
		}
	]);

	let scrollspyParent: HTMLElement | null = $state(null);

	// TBD: potential useful features to encaspulate the scroll into:
	// onMount, afterNavigate $effect, (beforeNavigate), (onNavigate), Attachment, onscrollend, derived, derived.by(), ...?

	let navBar: HTMLElement | null = $state(null);
	let navBarBottom: number = $state(0);

	// let contentArea: HTMLElement | null = $state(null);
	// let contentAreaTop: number = $state(0);
	// let contentAreaOffset: number = $state(0);

	// let locationHash: string = $state('');
	// TBD: include search parameters?
	type LocationPageAndHash = {
		page: string;
		hash: string;
	};
	let locationPageAndHash: LocationPageAndHash | null = $state(null);

	onMount(() => {
		// Polyfill for scrollend event (Safari doesn't support it yet)
		let scrollEndTimer: ReturnType<typeof setTimeout> | null = null;
		let cleanupScrollEndPolyfill: (() => void) | null = null;

		// Wait for scrollspyParent to be available
		if (scrollspyParent) {
			// Check if scrollend is supported
			const supportsScrollEnd = 'onscrollend' in scrollspyParent;

			if (!supportsScrollEnd) {
				// console.log('=== scrollend not supported - using polyfill ===');

				const handleScroll = () => {
					if (scrollEndTimer) {
						clearTimeout(scrollEndTimer);
					}
					scrollEndTimer = setTimeout(() => {
						const scrollEndEvent = new Event('scrollend', { bubbles: true });
						scrollspyParent?.dispatchEvent(scrollEndEvent);
					}, 150); // 150ms after scroll stops (slightly longer for reliability)
				};

				scrollspyParent.addEventListener('scroll', handleScroll, { passive: true });

				cleanupScrollEndPolyfill = () => {
					scrollspyParent?.removeEventListener('scroll', handleScroll);
					if (scrollEndTimer) {
						clearTimeout(scrollEndTimer);
						scrollEndTimer = null;
					}
				};
			}
		}

		// Reroute native history updates to SvelteKit to avoid router conflicts
		// const originalPush = history.pushState.bind(history);
		const originalReplace = history.replaceState.bind(history);
		// Capture native prototype methods to bypass SvelteKit's patched wrappers
		// const nativePush = History.prototype.pushState;
		const nativeReplace = History.prototype.replaceState;
		let bypassNativeOverride = false;
		// TBD: check if tyhis is needed at all?
		// history.pushState = (state: unknown, title: string, url?: string | URL | null) => {
		// 	if (bypassNativeOverride) {
		// 		// Call the native prototype directly to avoid warning wrappers
		// 		return nativePush.call(history, state, title, url ?? '');
		// 	}
		// 	const nextUrl = url instanceof URL ? url.toString() : typeof url === 'string' ? url : null;
		// 	if (nextUrl) {
		// 		bypassNativeOverride = true;
		// 		try {
		// 			pushState(nextUrl, page.state);
		// 		} finally {
		// 			bypassNativeOverride = false;
		// 		}
		// 	} else {
		// 		// Fallback to native method to avoid warnings
		// 		nativePush.call(history, state, title, url ?? '');
		// 	}
		// };
		// TBD: only catch navigation from scrollspy / FlyonUI here!
		history.replaceState = (state: unknown, title: string, url?: string | URL | null) => {
			if (bypassNativeOverride) {
				// Call the native prototype directly to avoid warning wrappers
				return nativeReplace.call(history, state, title, url ?? '');
			}
			const nextUrl = url instanceof URL ? url.toString() : typeof url === 'string' ? url : null;
			if (nextUrl) {
				bypassNativeOverride = true;

				// Detect FlyonUI scrollspy hash-only updates and convert to pushState
				const current = new URL(location.href);
				const next = new URL(nextUrl, location.href);
				const isSamePath = current.pathname === next.pathname && current.search === next.search;
				const isHashChange = current.hash !== next.hash;
				try {
					// FlyonUI scrollspy calls replaceState for hash changes - convert to pushState for history
					if (isSamePath && isHashChange) {
						// console.log('=== history.replaceState converted to pushState for hash change ===');
						pushState(nextUrl, page.state);
					} else {
						replaceState(nextUrl, page.state);
					}
				} finally {
					bypassNativeOverride = false;
				}
			} else {
				// Fallback to native method to avoid warnings
				nativeReplace.call(history, state, title, url ?? '');
			}
		};

		return () => {
			if (cleanupScrollEndPolyfill) {
				cleanupScrollEndPolyfill();
			}
			// history.pushState = originalPush;
			history.replaceState = originalReplace;
		};
	});

	// ********* remove navbar patches from here *********
	afterNavigate((navigation) => {
		// console.log('=== afterNavigate - navigation ===');
		navBarBottom =
			navBar && navBar.getBoundingClientRect().bottom > 0
				? navBar.getBoundingClientRect().bottom
				: 0;
		if (!location.hash) {
			// console.log('=== afterNavigate - scroll to TOP ===');
			locationPageAndHash = {
				page: navigation.to?.url.pathname || '',
				hash: ''
			};
			requestAnimationFrame(() => {
				scrollspyParent!.scrollTop = 0;
				scrollspyParent?.scrollTo({
					left: scrollspyParent.scrollLeft,
					top: scrollspyParent.scrollTop,
					behavior: 'smooth'
				});
			});
		}
	});

	const adjustScrollTopForNavBar = () => {
		// console.log('=== adjustScrollTopForNavBar ===');
		// Double requestAnimationFrame ensures layout has fully settled
		requestAnimationFrame(() => {
			requestAnimationFrame(() => {
				// Re-measure navbar height after layout settles
				navBarBottom =
					navBar && navBar.getBoundingClientRect().bottom > 0
						? navBar.getBoundingClientRect().bottom
						: 0;
				scrollspyParent!.scrollTop -= navBarBottom;
				scrollspyParent?.scrollTo({
					left: scrollspyParent.scrollLeft,
					top: scrollspyParent.scrollTop,
					behavior: 'smooth'
				});
			});
		});
	};

	const mainScrollEnd = (_event: Event) => {
		// console.log('=== onscrollend ===');
		// note: the SidebarFolder has "max-sm:[--scrollspy-offset:56px]",
		// which also affects the scrollspy offset calculation!
		const thisPageandHash: LocationPageAndHash = {
			page: page.url.pathname,
			hash: location.hash
		};
		if (locationPageAndHash?.hash !== thisPageandHash.hash && window.innerWidth >= 640) {
			locationPageAndHash = thisPageandHash;
			adjustScrollTopForNavBar();
		} else if (locationPageAndHash?.page !== thisPageandHash.page) {
			locationPageAndHash = thisPageandHash;
			adjustScrollTopForNavBar();
		}
		// contentAreaTop = contentArea ? contentArea.getBoundingClientRect().top : 0;
	};

	onMount(() => {
		// console.log('=== onMount ===');
		scrollspyParent!.scrollTo({
			left: scrollspyParent!.scrollLeft,
			top: scrollspyParent!.scrollTop,
			behavior: 'smooth'
		});
		if (page.url.hash) {
			const target = document.getElementById(page.url.hash.substring(1));
			// TBD: consider opening a potential collapsed parent sections here
			if (target) {
				const parentRect = scrollspyParent!.getBoundingClientRect();
				const targetRect = target.getBoundingClientRect();
				scrollspyParent!.scrollTop += targetRect.top - parentRect.top;
				scrollspyParent?.scrollTo({
					left: scrollspyParent.scrollLeft,
					top: scrollspyParent.scrollTop,
					behavior: 'smooth'
				});
			}
		}
	});

	const windowPopstateHandler = (_event: PopStateEvent) => {
		// console.log('=== 🪟 - popstate ===');
		if (page.url.hash) {
			const target = document.getElementById(location.hash.substring(1));
			// TBD: consider opening a potential collapsed parent sections here
			if (target) {
				const parentRect = scrollspyParent!.getBoundingClientRect();
				const targetRect = target.getBoundingClientRect();
				scrollspyParent!.scrollTop += targetRect.top - parentRect.top;
				scrollspyParent?.scrollTo({
					left: scrollspyParent.scrollLeft,
					top: scrollspyParent.scrollTop,
					behavior: 'smooth'
				});
			}
		}
		// locationHash = location.hash;
	};
	// ********* remove navbar patches until here *********

	// Hide / show  navbar on scroll down / up
	// let mainContent: HTMLDivElement | null = $state(null);
	let header: HTMLElement | null = $state(null);
	// let headerHeight: number = $state(0);
	// Set CSS variable for header height
	// $effect(() => {
	// 	// console.log(`=== header.offsetHeight ===`);
	// 	// console.log(headerHeight);
	// 	if (header) {
	// 		// get the complete height of the header, including margins, even if it's not visible:
	// 		const height =
	// 			header.offsetHeight +
	// 			parseFloat(getComputedStyle(header).marginTop) +
	// 			parseFloat(getComputedStyle(header).marginBottom);
	// 		console.log(`=== setting --header-height to ${height}px ===`);
	// 		document.documentElement.style.setProperty('--header-height', `${header.offsetHeight}px`);
	// 		// 	headerHeight =
	// 		// 		header.getBoundingClientRect().bottom > 0 ? header.getBoundingClientRect().bottom : 0;
	// 	}
	// });
	let previousScrollY = $derived.by(() => scrollspyParent?.scrollTop ?? 0);
	onMount(() => {
		document.documentElement.style.setProperty('--header-height', `${header?.offsetHeight}px`);
	});

	const windowResizeHandler = (_event: UIEvent) => {
		document.documentElement.style.setProperty('--header-height', `${header?.offsetHeight}px`);
	};
	const toggleTopNavBar = () => {
		const currentScrollY = scrollspyParent?.scrollTop ?? 0;
		if (navBar) {
			// console.log('=== toggleTopNavBar ===');
			// console.log(
			// 	`=== currentScrollY: ${currentScrollY} - previousScrollY: ${previousScrollY} ===`
			// );
			if (currentScrollY > previousScrollY) {
				// console.log(`=== Scrolling down - hide navbar - ${navBarBottom} ===`);
				// Scrolling down
				// navBar.style.transform = `translateY(-${navBarBottom}px)`;
				// navBar.style.transform = `translateY(-100%)`;
				navBar.classList.add('-mt-[var(--header-height)]');
				header?.classList.remove('mt-2');
				// navBar.classList.add(`mt-[-56px]`);
				// console.log(`=== navBarBottom: ${navBarBottom} ===`);
				// console.log(
				// 	`=== navBarBottom: ${document.documentElement.style.getPropertyValue('--navbar-bottom')} ===`
				// );
				// {`[--scrollspy-offset:${topoffset}]`.toString()}
				// navBar.classList.add(`mt-[-${navBarBottom}]`.toString());
				// works, but doesn't transition smoothly:
				// navBar.classList.add('hidden');
				// navBar.style.transform = `translateY(-110%)`;
			} else {
				// Scrolling up
				// navBar.style.transform = 'translateY(0)';
				// navBar.classList.remove(`mt-[-${navBarBottom}px]`.toString());
				// works, but doesn't transition smoothly:
				// navBar.classList.remove('hidden');
				navBar.classList.remove('-mt-[var(--header-height)]');
				header?.classList.add('mt-2');
			}
		}
		previousScrollY = currentScrollY;
	};
</script>

<svelte:window
	onpopstate={(event) => windowPopstateHandler(event)}
	onresize={(event) => windowResizeHandler(event)}
/>

{#snippet sidebarToggleButton(classes: string, overlayModifier: object)}
	<button
		type="button"
		class="btn btn-square btn-sm btn-outline btn-primary {classes}"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="collapsible-mini-sidebar"
		aria-label="Toggle Sidebar"
		{...overlayModifier}
	>
		<!-- data-overlay="#collapsible-mini-sidebar"
		data-overlay-options={ JSON.stringify({ "backdropClasses": "overlay-backdrop transition duration-300 fixed inset-0 bg-base-300/60 overflow-y-auto", "backdropParent": "#scrollspy" }) } -->
		<!-- <div id="collapsible-mini-sidebar-backdrop" data-overlay-backdrop-template="overlay-backdrop transition duration-300 fixed inset-0 bg-base-300/60 overflow-y-auto" style="z-index: 79;" class=""></div> -->
		<span
			class="icon-[material-symbols--menu-open-rounded] overlay-minified:hidden flex size-5 max-sm:hidden"
		></span>
		<span class="icon-[material-symbols--menu] overlay-minified:flex hidden size-5 max-sm:flex"
		></span>
	</button>
{/snippet}

{#snippet navbarPartItem(href: string, icon: string, text: string, textClasses?: string)}
	<li class="text-primary hidden items-center md:flex">
		<a {href} aria-label={text} class="flex items-center gap-1"
			><span class="{icon} size-5"></span>
			<span class={textClasses}>{text}</span>
		</a>
	</li>
{/snippet}

{#snippet sidebarPartItem(href: string, icon: string, text: string, listItemClasses?: string)}
	<li class="text-primary {listItemClasses}">
		<a {href}>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">{text}</span>
		</a>
	</li>
{/snippet}

<header bind:this={header} class="xs:mx-5 xs:mt-5 mt-2 w-screen px-2">
	<!-- bind:offsetHeight={headerHeight} -->
	<nav
		class="navbar rounded-box bg-base-200 shadow-shadow border-outline-variant sticky start-0 top-0 z-1 flex justify-between border-1 border-b shadow-md transition-all duration-300 max-sm:h-14 max-sm:px-3 md:items-center"
		bind:this={navBar}
	>
		<!-- {@attach updateNavbarBottom} -->
		<div class="navbar-start rtl:[--placement:bottom-end]">
			<ul class="menu menu-horizontal flex flex-nowrap items-center">
				{@render sidebarToggleButton('hidden sm:flex', {
					'data-overlay-minifier': '#collapsible-mini-sidebar'
				})}
				{@render sidebarToggleButton('sm:hidden', {
					'data-overlay': '#collapsible-mini-sidebar'
				})}
				{@render navbarPartItem('/docs', 'icon-[oui--documentation]', 'Docs')}
				{@render navbarPartItem(
					'/playground',
					'icon-[mdi--playground-seesaw]',
					'Playground',
					'hidden lg:block'
				)}
				<Guard>
					{@render navbarPartItem(
						'/dashboard',
						'icon-[material-symbols--dashboard-outline-rounded]',
						'Dashboard',
						'hidden xl:block'
					)}
				</Guard>
				<!-- {@render navbarPartItem(
						'/features',
						'icon-[mdi--feature-highlight]',
						'Features',
						'hidden xl:block'
					)}
					{@render navbarPartItem('/apps', 'icon-[tabler--apps]', 'Apps', 'hidden xl:block')}
					{@render navbarPartItem(
						'/construction',
						'icon-[maki--construction]',
						'Construction',
						'hidden xl:block'
					)} -->
			</ul>
		</div>
		<Logo />
		<div class="navbar-end">
			<button
				class="btn btn-sm btn-text btn-circle text-primary size-8.5 md:hidden"
				aria-label="Search"
			>
				<span class="icon-[tabler--search] size-5"></span>
			</button>
			<div class="input mx-2 max-w-56 rounded-full max-md:hidden">
				<span class="icon-[tabler--search] text-base-content/80 my-auto me-3 size-5 shrink-0"
				></span>
				<label class="sr-only" for="searchInput">Search</label>
				<input type="search" class="grow" placeholder="Search" id="searchInput" />
			</div>
			<div
				class="dropdown flex items-center [--auto-close:inside] rtl:[--placement:bottom-end]"
				{@attach initDropdown}
			>
				<span
					id="dropdown-menu-icon-user"
					class="dropdown-toggle {!loggedIn ? 'icon-[fa6-solid--user] bg-secondary size-5' : ''}"
					role="button"
					aria-haspopup="menu"
					aria-expanded="false"
					aria-label="User Menu"
				>
					{#if loggedIn}
						<img
							class="not-hover:mask-radial-t-0% h-10 min-w-10 rounded-full not-hover:mask-radial-from-40%"
							src={resolve('/apiproxies/msgraph') + '?endpoint=/me/photo/$value'}
							alt="you"
						/>
					{/if}
				</span>
				<ul
					class="dropdown-menu bg-base-200 text-secondary shadow-outline dropdown-open:opacity-100 hidden shadow-md"
					role="menu"
					aria-orientation="vertical"
					aria-labelledby="dropdown-menu-icon-user"
				>
					<ArtificialIntelligencePicker
						{updateProfileAccount}
						{saveProfileAccount}
						bind:artificialIntelligenceForm
						bind:artificialIntelligenceConfiguration
					/>
					<li>
						<hr class="border-outline -mx-2 my-5" />
					</li>
					<ThemePicker
						{updateProfileAccount}
						{saveProfileAccount}
						bind:themeForm
						bind:mode
						bind:themeConfiguration
					/>
					<li>
						<hr class="border-outline -mx-2 my-5" />
					</li>
					<li class="flex items-center gap-2">
						<button
							aria-label="show Modal"
							type="button"
							class="dropdown-item dropdown-close"
							aria-haspopup="dialog"
							aria-expanded="false"
							aria-controls="welcome-modal"
							data-overlay="#welcome-modal"
						>
							<span class="icon-[tabler--eye] bg-secondary size-5"></span>
							<span class="text-secondary grow">Show welcome modal</span>
						</button>
					</li>
				</ul>
			</div>
			<div class="hidden items-center sm:flex md:ml-2">
				<LoginOutButton {loggedIn} />
			</div>
		</div>
	</nav>
</header>

<main
	bind:this={scrollspyParent}
	id="scrollspy-scrollable-parent"
	class="border-error h-screen w-screen overflow-x-scroll overflow-y-auto border border-4"
	onscrollend={mainScrollEnd}
	onscroll={toggleTopNavBar}
	use:applyTheming
>
	<!-- bind:session={data.session} -->
	<WelcomeModal
		bind:session
		bind:artificialIntelligenceConfiguration
		bind:themeConfiguration
		bind:mode
		{updateProfileAccount}
		{saveProfileAccount}
	/>

	<!-- TBD: put sidebar into component -->
	<aside
		id="collapsible-mini-sidebar"
		class="overlay overlay-minified:w-19 overlay-open:translate-x-0 drawer drawer-start bg-base-150 border-base-content/20 hidden w-66 border-e [--auto-close:sm] sm:absolute sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
		tabindex="-1"
		{@attach initOverlay}
	>
		<div class="mx-7 flex h-26 flex-row items-center justify-between pt-7">
			<div class="hidden sm:block">
				{@render sidebarToggleButton('hidden sm:flex', {
					'data-overlay-minifier': '#collapsible-mini-sidebar'
				})}
			</div>
			<div class="overlay-minified:hidden">
				<Logo />
			</div>
		</div>
		<div class="drawer-body px-2 pt-4">
			<ul class="menu p-0">
				<!-- <li><a href={resolve('/(layout)/playground/page2')}>Page 2 - top</a></li>
				<li><a href={resolve('/(layout)/playground/page2') + '#pg2loreum1'}>Page 2 - Lor. 1</a></li>
				<li><a href={resolve('/(layout)/playground/page2') + '#pg2loreum2'}>Page 2 - Lor. 2</a></li>
				<li><a href={resolve('/(layout)/playground/page2') + '#pg2loreum4'}>Page 2 - Lor. 4</a></li> -->
				{@render sidebarPartItem('/', 'icon-[material-symbols--home-outline-rounded]', 'Home')}
				{@render sidebarPartItem('/docs', 'icon-[oui--documentation]', 'Docs', 'md:hidden')}
				{@render sidebarPartItem(
					'/playground',
					'icon-[mdi--playground-seesaw]',
					'Playground',
					'md:hidden'
				)}
				<Guard>
					<!-- <hr class="border-outline -mx-2 my-3" /> -->
					{@render sidebarPartItem(
						'/dashboard',
						'icon-[material-symbols--dashboard-outline-rounded]',
						'Dashboard',
						'md:hidden'
					)}
				</Guard>
				<!-- {@render sidebarPartItem(
					'/features',
					'icon-[mdi--feature-highlight]',
					'Features',
					'md:hidden'
				)}
				{@render sidebarPartItem('/apps', 'icon-[tabler--apps]', 'Apps', 'md:hidden')}
				{@render sidebarPartItem(
					'/construction',
					'icon-[maki--construction]',
					'Construction',
					'md:hidden'
				)} -->
				<li>
					<div class="items-center sm:hidden md:ml-2">
						<LoginOutButton {loggedIn} />
					</div>
				</li>
			</ul>
			<div class="divider"></div>
			<ul class="menu p-0">
				{#each sidebarLinks as sidebarItem (sidebarItem.id)}
					<SidebarItem
						content={{ ...sidebarItem, pathname: sidebarItem.pathname || page.url.pathname }}
						topLevel={true}
						{scrollspyParent}
					/>
					<!-- topoffset={navBarBottom} -->
					<!-- topoffset={internalNavigationTarget} -->
					<!-- topoffset={navBarBottom} -->
					<!-- topoffset={`[--scrollspy-offset:${navBarBottom + 8}]`} -->
				{/each}
				<Guard>
					{#each protectedSidebarLinks as protectedSidebarItem (protectedSidebarItem.id)}
						<SidebarItem
							content={{
								...protectedSidebarItem,
								pathname: protectedSidebarItem.pathname || page.url.pathname
							}}
							topLevel={true}
							{scrollspyParent}
						/>
						<!-- topoffset={navBarBottom} -->
					{/each}
				</Guard>
				{#if debug}
					{#each debugSidebarLinks as debugSidebarItem (debugSidebarItem.id)}
						<SidebarItem
							content={{
								...debugSidebarItem,
								pathname: debugSidebarItem.pathname || page.url.pathname
							}}
							topLevel={true}
							{scrollspyParent}
						/>
						<!-- topoffset={navBarBottom} -->
					{/each}
				{/if}
			</ul>
		</div>
		<div class="mb-2 flex items-center gap-1">
			<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
			<input
				type="checkbox"
				class="switch-neutral switch"
				bind:checked={debug}
				id="debugSwitcher"
			/>
		</div>
		<!-- {navBarBottom}
		<br />
		{locationPageAndHash?.page}{locationPageAndHash?.hash}
		<br /> -->
	</aside>
	<div class="bg-base-100 xs:mx-5 xs:mt-5 mt-2 w-screen px-2 sm:h-full">
		<!-- TBD: put navbar into component -->
		<!-- <div class="h-full"> -->

		<!-- </div> -->

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
