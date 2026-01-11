<script lang="ts">
	import type { LayoutData } from './$types';
	import { SessionStatus } from '$lib/session';
	import { Variant, Theming, type ColorConfig } from '$lib/theming';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
	import type { Action } from 'svelte/action';
	import { writable } from 'svelte/store';
	import { onMount, setContext, type Snippet } from 'svelte';
	import { page } from '$app/state';
	import Guard from '$components/Guard.svelte';
	import { initDropdown, initOverlay } from '$lib/userInterface';
	import ThemePicker from '../../../components/ThemePicker.svelte';
	import ArtificialIntelligencePicker from '../../../components/ArtificialIntelligencePicker.svelte';
	import { themeStore } from '$lib/stores';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { resolve } from '$app/paths';
	import WelcomeModal from '../../../../WelcomeModal.svelte';
	import { goto, afterNavigate } from '$app/navigation';
	import type { SidebarItemContent, Session } from '$lib/types';
	import SidebarItem from './SidebarItem.svelte';
	import LoginOutButton from '../../../../LoginOutButton.svelte';
	import Logo from '../../../../Logo.svelte';
	import { scrollY } from 'svelte/reactivity/window';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();

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
	// type SidebarLinkContent = {
	// 	id: string;
	// 	name: string;
	// 	pathname?: string;
	// 	hash?: string;
	// 	icon: string;
	// 	// TBD: implement <Guard> around SidebarItem based on this property!
	// 	guarded?: boolean;
	// };

	// type SidebarFolderContent = SidebarLinkContent & {
	// 	items: SidebarItemContent[];
	// };
	// export type SidebarFolderContent = {
	// 	id: string;
	// 	name: string;
	// 	pathname?: string;
	// 	hash?: string;
	// 	icon: string;
	// 	items: SidebarItemContent[];
	// };
	// type SidebarItemContent = SidebarFolderContent | SidebarLinkContent;

	// Sidebar:
	// let sidebarLinks: SidebarItemContent[] = $state([
	// 	{
	// 		name: 'Docs',
	// 		pathname: resolve('/(plain)/docs'),
	// 		icon: 'icon-[oui--documentation]',
	// 		id: 'docs',
	// 		items: []
	// 	},
	// 	{
	// 		name: 'Playground',
	// 		pathname: resolve('/(layout)/playground'),
	// 		icon: 'icon-[mdi--playground-seesaw]',
	// 		id: 'playground',
	// 		items: [
	// 			{
	// 				name: 'Overview',
	// 				pathname: resolve('/(layout)/playground') + '#top',
	// 				icon: 'icon-[mdi--playground-seesaw]',
	// 				id: 'overview'
	// 			},
	// 			{
	// 				name: 'User Interface',
	// 				pathname: resolve('/(layout)/playground/user-interface'),
	// 				icon: 'icon-[mdi--monitor-dashboard]',
	// 				id: 'user-interface',
	// 				items: []
	// 			},
	// 			{
	// 				name: 'Components',
	// 				pathname: resolve('/(layout)/playground/components') + '?prod=false&develop=true',
	// 				icon: 'icon-[tabler--components]',
	// 				id: 'components',
	// 				items: []
	// 			},
	// 			{
	// 				name: 'Design',
	// 				pathname: resolve('/(layout)/playground/design'),
	// 				icon: 'icon-[fluent--design-ideas-20-regular]',
	// 				id: 'design',
	// 				items: [
	// 					{
	// 						name: 'Backgrounds',
	// 						icon: 'icon-[mdi--palette-outline]',
	// 						hash: '#backgrounds-and-surfaces',
	// 						id: 'backgrounds'
	// 					},
	// 					{
	// 						name: 'Foregrounds',
	// 						icon: 'icon-[mdi--palette-outline]',
	// 						hash: '#foregrounds',
	// 						id: 'foregrounds'
	// 					},
	// 					{
	// 						name: 'Components',
	// 						icon: 'icon-[mdi--palette-outline]',
	// 						hash: '#components',
	// 						id: 'components'
	// 					},
	// 					{
	// 						name: 'Playground',
	// 						icon: 'icon-[mdi--playground-seesaw]',
	// 						hash: '#design-playground',
	// 						id: 'design-playground'
	// 					},
	// 					{
	// 						name: 'Building Blocks',
	// 						icon: 'icon-[clarity--blocks-group-line]',
	// 						hash: '#design-building-blocks',
	// 						id: 'design-building-blocks',
	// 						items: [
	// 							{
	// 								name: 'FlyonUI',
	// 								icon: 'icon-[mingcute--arrows-up-fill]',
	// 								pathname: resolve('/(layout)/playground/design/flyonui'),
	// 								id: 'flyonui'
	// 							},
	// 							{
	// 								name: 'Material Design',
	// 								icon: 'icon-[mdi--material-design]',
	// 								pathname: resolve('/(layout)/playground/design/materialdesign'),
	// 								id: 'material-design'
	// 							},
	// 							{
	// 								name: 'Svelte',
	// 								icon: 'icon-[tabler--brand-svelte]',
	// 								pathname: resolve('/(layout)/playground/design/svelte'),
	// 								id: 'svelte'
	// 							}
	// 						]
	// 					}
	// 				]
	// 			},
	// 			{
	// 				name: 'Data Flow & Navigation',
	// 				pathname: resolve('/(layout)/playground/dataflow'),
	// 				icon: 'icon-[iconoir--data-transfer-both]',
	// 				id: 'dataflow'
	// 			},
	// 			{
	// 				name: 'Backend Schema',
	// 				pathname: resolve('/(layout)/playground/backend-schema'),
	// 				icon: 'icon-[file-icons--openapi]',
	// 				id: 'backend-schema'
	// 			},
	// 			{
	// 				name: 'Counter',
	// 				pathname: resolve('/(layout)/playground/counter'),
	// 				icon: 'icon-[mdi--counter]',
	// 				id: 'counter'
	// 			},
	// 			{
	// 				name: 'Core',
	// 				pathname: resolve('/(layout)/playground/core'),
	// 				icon: 'icon-[streamline-ultimate--computer-chip-core]',
	// 				id: 'core'
	// 			},
	// 			{
	// 				name: 'Websockets',
	// 				pathname: resolve('/(layout)/playground/websockets'),
	// 				icon: 'icon-[solar--socket-linear]',
	// 				id: 'websockets'
	// 			}
	// 		]
	// 	}
	// 	// {
	// 	// 	name: 'Apps',
	// 	// 	pathname: resolve('/(layout)/(protected)/dashboard'),
	// 	// 	icon: 'icon-[material-symbols--dashboard-outline-rounded]',
	// 	// 	id: 'apps',
	// 	// 	items: []
	// 	// },
	// ]);

	// let protectedSidebarLinks: SidebarItemContent[] = $state([
	// 	{
	// 		name: 'Dashboard',
	// 		pathname: resolve('/(layout)/(protected)/dashboard'),
	// 		icon: 'icon-[material-symbols--dashboard-outline-rounded]',
	// 		id: 'dashboard',
	// 		items: [
	// 			{
	// 				name: 'Overview',
	// 				pathname: resolve('/(layout)/(protected)/dashboard') + '#top',
	// 				icon: 'icon-[material-symbols--dashboard-outline-rounded]',
	// 				id: 'overview'
	// 			},
	// 			{
	// 				name: 'Demo Resources',
	// 				pathname: resolve('/(layout)/(protected)/dashboard/backend-demo-resource'),
	// 				icon: 'icon-[grommet-icons--resources]',
	// 				id: 'demo-resource',
	// 				items: [
	// 					{
	// 						name: 'Rest API',
	// 						pathname: resolve('/(layout)/(protected)/dashboard/backend-demo-resource/restapi'),
	// 						icon: 'icon-[dashicons--rest-api]',
	// 						id: 'demo-resource-restapi'
	// 					},
	// 					{
	// 						name: 'Socket IO',
	// 						pathname: resolve('/(layout)/(protected)/dashboard/backend-demo-resource/socketio'),
	// 						icon: 'icon-[tabler--brand-socket-io]',
	// 						id: 'demo-resource-socketio'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				name: 'Hierarchical Resources',
	// 				pathname: resolve('/(layout)/(protected)/dashboard/backend-protected-hierarchy'),
	// 				icon: 'icon-[fluent-mdl2--family]',
	// 				id: 'hierarchical-resources'
	// 			},
	// 			{
	// 				name: 'Identities',
	// 				// pathname: resolve('/(layout)/(protected)/dashboard/identities'),
	// 				icon: 'icon-[material-symbols--identity-platform-outline-rounded]',
	// 				id: 'identities',
	// 				items: [
	// 					{
	// 						name: 'All identities',
	// 						pathname: resolve('/(layout)/(protected)/dashboard/identities'),
	// 						icon: 'icon-[mdi--account-multiple-outline]',
	// 						id: 'identities-all'
	// 					},
	// 					{
	// 						name: 'Microsoft',
	// 						pathname: resolve('/(layout)/(protected)/dashboard/msgraph'),
	// 						icon: 'icon-[fluent--person-20-filled]',
	// 						id: 'identities-microsoft'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				name: 'Socket.IO',
	// 				pathname: resolve('/(layout)/(protected)/dashboard/socketio'),
	// 				icon: 'icon-[tabler--brand-socket-io]',
	// 				id: 'socketio'
	// 			}
	// 		]
	// 	}
	// ]);

	let debugSidebarLinks: SidebarItemContent[] = $state([
		{
			name: 'Page 1',
			pathname: resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page1'),
			icon: 'icon-[tabler--user]',
			id: 'page1',
			items: []
		},
		{
			name: 'Page 2',
			pathname: resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page2'),
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
			pathname: resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page3'),
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
			pathname: resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4'),
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
					pathname: resolve(
						'/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4/page4-1'
					),
					id: 'page4p1',
					items: [
						{
							id: 'page4p1-loreum1',
							name: 'Loreum 1 pg4.1',
							icon: 'icon-[mdi--text]',
							pathname: resolve(
								'/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4/page4-1'
							),
							hash: '#loreum1',
							items: [
								{
									id: 'page4p1p1',
									name: 'Page 4.1.1',
									icon: 'icon-[mdi--text]',
									pathname: resolve(
										'/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4/page4-1/page4-1-1'
									)
								},
								{
									id: 'page4p1p2',
									name: 'Page 4.1.2',
									icon: 'icon-[mdi--text]',
									pathname: resolve(
										'/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4/page4-1/page4-1-2'
									)
								}
							]
						},
						{
							id: 'page4p1-loreum2',
							name: 'Loreum 2 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve(
								'/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4/page4-1'
							),
							hash: '#loreum2'
						}
					]
				},
				{
					name: 'Sub-page 4.2',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					pathname: resolve(
						'/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4/page4-2'
					),
					id: 'page4p2',
					items: [
						{
							id: 'page4p2-loreum1',
							name: 'Loreum 1 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve(
								'/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4/page4-2'
							),
							hash: '#loreum1'
						},
						{
							id: 'page4p2-loreum2',
							name: 'Loreum 2 pg4.2',
							icon: 'icon-[mdi--text]',
							pathname: resolve(
								'/(layout)/playground/user-interface/navbar/custom-scrolltracking/page4/page4-2'
							),
							hash: '#loreum2'
						}
					]
				},
				{
					id: 'page4-loreum5',
					name: 'Loreum 5',
					icon: 'icon-[mdi--text]',
					hash: '#loreum5'
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
			pathname: resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page5'),
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
					targetElement.scrollIntoView({ behavior: 'smooth' });
				}
				handleIntentionalNavigation();
			}, 100);
		} else {
			// Scroll to top if no hash
			window.scrollTo({ top: 0, behavior: 'smooth' });
			handleIntentionalNavigation();
		}
	});

	let navBar: HTMLElement | null = $state(null);
	let navBarBottom: number = $state(0);

	// Hide / show  navbar on scroll down / up
	let header: HTMLElement | null = $state(null);
	let previousScrollY = $state(scrollY.current ?? 0);
	let intentionalNavigationInProgress = $state(false);

	// Show navbar and mark navigation as intentional:
	const handleIntentionalNavigation = () => {
		if (header) {
			// Show navbar when browser back/forward is used
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
		// Don't hide navbar during intentional navigation (sidebar clicks, browser back/forward)
		if (!intentionalNavigationInProgress) {
			// console.log('=== toggleTopNavBar ===');
			// const currentScrollY = scrollspyParent?.scrollTop ?? 0;
			// see https://www.w3schools.com/howto/howto_js_navbar_hide_scroll.asp
			const currentScrollY = scrollY.current ?? 0;
			// if (navBar) {
			if (header) {
				if (currentScrollY > previousScrollY) {
					// Scrolling down removes navbar
					// navBar.classList.add('-mt-[var(--header-height)]');
					header.classList.remove('mt-2');
					header.style.top = `-${header.offsetHeight}px`;
					navBarBottom = 0;
				} else {
					// Scrolling up shows navbar
					// navBar.classList.remove('-mt-[var(--header-height)]');
					header.classList.add('mt-2');
					header.style.top = '0';
					navBarBottom = header.offsetHeight;
				}
			}
			previousScrollY = currentScrollY;
		}
	};

	// onMount(() => {
	// 	document.addEventListener('beforeScroll.scrollspy', showNavbarOnSidebarClick);
	// });
</script>

<svelte:window
	onresize={(event) => windowResizeHandler(event)}
	onscroll={toggleTopNavBar}
	onscrollend={() => {
		intentionalNavigationInProgress = false;
	}}
	onpopstate={handleIntentionalNavigation}
/>

<svelte:body use:applyTheming />

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

<header
	bind:this={header}
	class="xs:mx-5 xs:mt-5 fixed z-1 mt-2 w-screen px-2 transition-all duration-300"
>
	<!-- TBD: put navbar into component -->
	<nav
		class="navbar rounded-box shadow-shadow border-outline-variant bg-base-200 start-0 top-0 z-1 flex justify-between border-1 border-b px-3 shadow-md transition-all duration-300 max-sm:h-14 md:items-center"
		bind:this={navBar}
	>
		<!-- bg-transparent -->
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

<!-- class="h-screen w-screen overflow-x-scroll overflow-y-auto" -->
<!-- bind:this={scrollspyParent} -->
<!-- use:applyTheming -->
<!-- id="scrollspy-scrollable-parent" -->
<!-- onscrollend={mainScrollEnd} -->
<main
	class="static w-screen transition-[padding-top] duration-300"
	style="padding-top: {navBarBottom + 4}px;"
>
	<!-- onscroll={toggleTopNavBar} -->
	<!-- class="border-error h-screen w-screen overflow-x-scroll overflow-y-auto border border-4" -->
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
	<!-- sm:absolute -->
	<aside
		id="collapsible-mini-sidebar"
		class="overlay overlay-minified:w-19 overlay-open:translate-x-0 drawer drawer-start bg-base-150 border-base-content/20 start-0 top-0 hidden w-66 border-e [--auto-close:sm] sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
		tabindex="-1"
		{@attach initOverlay}
	>
		<div class="mx-7 flex h-24 flex-row items-center justify-between md:h-26">
			<div class="hidden sm:block">
				{@render sidebarToggleButton('hidden sm:flex', {
					'data-overlay-minifier': '#collapsible-mini-sidebar'
				})}
			</div>
			<div class="overlay-minified:hidden">
				<Logo />
			</div>
		</div>
		<div class="drawer-body px-2">
			<ul class="menu p-0">
				<!-- <li><a href={resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page2')}>Page 2 - top</a></li>
				<li><a href={resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page2') + '#pg2loreum1'}>Page 2 - Lor. 1</a></li>
				<li><a href={resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page2') + '#pg2loreum2'}>Page 2 - Lor. 2</a></li>
				<li><a href={resolve('/(layout)/playground/user-interface/navbar/custom-scrolltracking/page2') + '#pg2loreum4'}>Page 2 - Lor. 4</a></li> -->
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
				<!-- {#each sidebarLinks as sidebarItem (sidebarItem.id)} -->
				<!-- TBD: remove topoffset -->
				<!-- <SidebarItem
						content={{ ...sidebarItem, pathname: sidebarItem.pathname || page.url.pathname }}
						topLevel={true}
						{scrollspyParent}
					/> -->
				<!-- {scrollspyParent} -->
				<!-- topoffset={navBarBottom} -->
				<!-- topoffset={internalNavigationTarget} -->
				<!-- topoffset={navBarBottom} -->
				<!-- topoffset={`[--scrollspy-offset:${navBarBottom + 8}]`} -->
				<!-- {/each} -->
				<!-- <Guard> -->
				<!-- {#each protectedSidebarLinks as protectedSidebarItem (protectedSidebarItem.id)} -->
				<!-- <SidebarItem
							content={{
								...protectedSidebarItem,
								pathname: protectedSidebarItem.pathname || page.url.pathname
							}}
							topLevel={true}
							{scrollspyParent}
						/> -->
				<!-- {scrollspyParent} -->
				<!-- topoffset={navBarBottom} -->
				<!-- {/each} -->
				<!-- </Guard> -->

				{#each debugSidebarLinks as debugSidebarItem (debugSidebarItem.id)}
					<SidebarItem
						content={{
							...debugSidebarItem,
							pathname: debugSidebarItem.pathname || page.url.pathname
						}}
						topLevel={true}
					/>
					<!-- {scrollspyParent} -->
				{/each}
				<!-- {#each Array(50) as _, index}
					<li>Filler Item {index + 1}</li>
				{/each} -->
			</ul>
			<!-- <ul data-scrollspy="#scrollspy" data-scrollspy-scrollable-parent="#app-body">
				<li>
					<a
						href="./page2#pg2loreum2"
						class="text-base-content/80 hover:text-base-content scrollspy-active:text-primary block py-0.5 font-medium"
					>
						Page 2 - Loreum 2
					</a>
				</li>
			</ul> -->
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
		scrollY: {scrollY.current}
		<br />
		navBarBottom: {navBarBottom}
		<!-- {navBarBottom}
		<br />
		{locationPageAndHash?.page}{locationPageAndHash?.hash}
		<br /> -->
	</aside>
	<div class="bg-base-100 xs:mx-5 xs:mt-5 h-screen w-screen px-2">
		<!-- style="padding-top: {navBarBottom}px;" -->
		<div
			class="sm:overlay-minified:ps-19 overlay-open:ps-0 space-y-4 pt-2 transition-all duration-300 sm:mx-2 sm:mt-2 sm:ps-66"
		>
			<!-- id="scrollspy" -->
			<!-- bind:this={contentArea} -->
			{@render children?.()}
			<!-- <div class="mt-100">Spaceholder</div>
			<a href={resolve('/(layout)/playground/page2') + '#pg2loreum2'}>Page2 Loreum2</a> -->
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
