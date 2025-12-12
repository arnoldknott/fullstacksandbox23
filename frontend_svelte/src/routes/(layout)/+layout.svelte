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
	import ThemePicker from './playground/components/ThemePicker.svelte';
	import ArtificialIntelligencePicker from './playground/components/ArtificialIntelligencePicker.svelte';
	import { themeStore } from '$lib/stores';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { resolve } from '$app/paths';
	import WelcomeModal from './WelcomeModal.svelte';
	import {
		afterNavigate,
		replaceState,
		pushState
		// onNavigate,
		// beforeNavigate,
		// goto
	} from '$app/navigation';
	import type { SidebarItemContent } from '$lib/types';
	import SidebarItem from './SidebarItem.svelte';
	import LoginOutButton from './LoginOutButton.svelte';
	import Logo from './Logo.svelte';
	import type { Attachment } from 'svelte/attachments';
	// import { scrollY } from 'svelte/reactivity/window';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	let userUnregistered = $derived(
		!data.session?.loggedIn
			? false
			: data.session?.status === SessionStatus.REGISTERED
				? false
				: true
	);

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
				// { name: 'Overview', pathname: resolve('/(layout)/playground'), icon: 'icon-[mdi--playground-seesaw]', hash: '#top', id: 'overview' },
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
						// {
						// 	name: 'Playground',
						// 	icon: 'icon-[mdi--playground-seesaw]',
						// 	hash: '#design-playground',
						// 	id: 'design-playground'
						// },
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
					hash: '#loreum1'
				},
				{
					id: 'page2-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#sub-category',
					id: 'page2-sub-category',
					items: [
						{
							id: 'page2-loreum3',
							name: 'Loreum 3',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3'
						},
						{
							id: 'page2-loreum4',
							name: 'Loreum 4',
							icon: 'icon-[mdi--text]',
							hash: '#loreum4'
						}
					]
				},
				{
					id: 'page2-loreum5',
					name: 'Loreum 5',
					icon: 'icon-[mdi--text]',
					hash: '#loreum5'
				},
				{
					id: 'page2-loreum6',
					name: 'Loreum 6',
					icon: 'icon-[mdi--text]',
					hash: '#loreum6'
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
					hash: '#loreum1'
				},
				{
					id: 'page3-loreum2',
					name: 'Loreum 2',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2'
				},
				{
					id: 'page3-loreum2a',
					name: 'Loreum 2a',
					icon: 'icon-[mdi--text]',
					hash: '#loreum2a'
				},
				{
					name: 'Sub category',
					icon: 'icon-[material-symbols--folder-outline-rounded]',
					hash: '#sub-category-page3',
					id: 'page3-sub-category',
					items: [
						{
							id: 'page3-loreum3p1',
							name: 'Loreum 3.1',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3p1'
						},
						{
							id: 'page3-loreum3p2',
							name: 'Loreum 3.2',
							icon: 'icon-[mdi--text]',
							hash: '#loreum3p2'
						}
					]
				},
				{
					id: 'page3-loreum4',
					name: 'Loreum 4',
					icon: 'icon-[mdi--text]',
					hash: '#loreum4'
				},
				{
					id: 'page3-loreum5',
					name: 'Loreum 5',
					icon: 'icon-[mdi--text]',
					hash: '#loreum5'
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
		// {
		// 	name: 'Apps',
		// 	pathname: resolve('/(layout)/(protected)/dashboard'),
		// 	icon: 'icon-[material-symbols--dashboard-outline-rounded]',
		// 	id: 'apps',
		// 	items: []
		// },
	]);

	let scrollspyParent: HTMLElement | null = $state(null);

	// TBD: potential useful features to encaspulate the scroll into:
	// onMount, afterNavigate $effect, (beforeNavigate), (onNavigate), Attachment, onscrollend, derived, derived.by(), ...?

	// const adjustContentAreaOffset = () => {
	// 	navBarBottom = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
	// 	contentAreaTop = contentArea ? contentArea.getBoundingClientRect().top : 0;
	// 	if (navBarBottom > 0 && contentAreaTop < navBarBottom)
	// 	{
	// 		contentAreaOffset = navBarBottom;
	// 	}
	// };

	// beforeNavigate(({to}) =>{
	// 	if(to && to.url) {
	// 		pushState(to.url, page.state);
	// 	}
	// })

	// afterNavigate(async ({ from, to }) => {
	// 	console.log('=== layout - afterNavigate ===');
	// 	// reset scrolling to zero, on internal navigation, if no hash is present:
	// 	if (!to?.url.hash) {
	// 		// console.log('=== layout - afterNavigate - scroll to TOP ===');
	// 		scrollspyParent!.scrollTop = 0;
	// 		scrollspyParent!.scrollTo({
	// 			left: scrollspyParent!.scrollLeft,
	// 			top: scrollspyParent!.scrollTop,
	// 			behavior: 'smooth'
	// 		});
	// 	}
	// 	else if (from?.url.pathname === to?.url.pathname) {
	// 		// console.log('=== layout - afterNavigate - hash-FROM ===');
	// 		// console.log(from!.url.hash.substring(1));
	// 		const targetFrom = document.getElementById(from!.url.hash.substring(1));
	// 		// TBD: consider opening a potential collapsed parent sections here
	// 		if (targetFrom) {
	// 			const targetRectFrom = targetFrom.getBoundingClientRect();
	// 			// This one prevents scrollspy dispatchEvent error on mount:
	// 			requestAnimationFrame(() => {
	// 				const targetScrollTop = targetRectFrom.top;
	// 				scrollspyParent!.scrollTop = targetScrollTop;
	// 				// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
	// 				scrollspyParent?.scrollTo({
	// 					left: scrollspyParent.scrollLeft,
	// 					top: scrollspyParent.scrollTop,
	// 					behavior: 'instant'
	// 				});
	// 			})
	// 		}
	// 		await tick()
	// 		// console.log('=== layout - afterNavigate - hash-TO ===');
	// 		// console.log(to!.url.hash.substring(1));
	// 		const targetTo = document.getElementById(to!.url.hash.substring(1));
	// 		// TBD: consider opening a potential collapsed parent sections here
	// 		if (targetTo) {
	// 			const targetRectTo = targetTo.getBoundingClientRect();
	// 			// This one prevents scrollspy dispatchEvent error on mount:
	// 			requestAnimationFrame(() => {
	// 				const targetScrollTop = targetRectTo.top;
	// 				scrollspyParent!.scrollTop = targetScrollTop;
	// 				// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
	// 				// console.log('=== layout - afterNavigate - scroll to hash - SMOOTHLY ===');
	// 				scrollspyParent?.scrollTo({
	// 					left: scrollspyParent.scrollLeft,
	// 					top: scrollspyParent.scrollTop,
	// 					behavior: 'smooth'
	// 				});
	// 			})
	// 		}
	// 	}

	// 	// navBarBottom = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
	// 	// contentAreaTop = contentArea ? contentArea.getBoundingClientRect().top : 0;
	// 	// console.log("=== layout - afterNavigate - old navBarBottom ===");
	// 	// console.log(navBarBottom);
	// 	// contentAreaOffset = contentAreaTop - navBarBottom;
	// 	// adjustContentAreaOffset();

	// 	// else {
	// 	// 	const target = document.getElementById(to!.url.hash.substring(1));
	// 	// 	// TBD: consider opening a potential collapsed parent sections here
	// 	// 	if (target) {
	// 	// 		const targetRect = target.getBoundingClientRect();
	// 	// 		// This one prevents scrollspy dispatchEvent error on mount:
	// 	// 		console.log('=== layout - afterNavigate - scroll to hash ===');
	// 	// 		requestAnimationFrame(() => {
	// 	// 			const targetScrollTop = targetRect.top;
	// 	// 			scrollspyParent!.scrollTop = targetScrollTop;
	// 	// 			// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
	// 	// 			scrollspyParent?.scrollTo({
	// 	// 				left: scrollspyParent.scrollLeft,
	// 	// 				top: scrollspyParent.scrollTop,
	// 	// 				behavior: 'smooth'
	// 	// 			});
	// 	// 		})
	// 	// 		// navBarBottomPrevious = navBarBottom;

	// 	// 		await tick()
	// 	// 		requestAnimationFrame(() => {
	// 	// 			navBarBottom = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
	// 	// 			console.log("=== layout - afterNavigate - new navBarBottom ===");
	// 	// 			console.log(navBarBottom);
	// 	// 			if (navBarBottom > 0) {
	// 	// 				scrollspyParent!.scrollTop += navBarBottom;
	// 	// 				scrollspyParent?.scrollTo({
	// 	// 					left: scrollspyParent.scrollLeft,
	// 	// 					top: scrollspyParent.scrollTop,
	// 	// 					behavior: 'smooth'
	// 	// 				});
	// 	// 		}
	// 	// 		});

	// 	// 	}
	// 	// }
	// 	// // else{
	// 	// // 	const target = document.getElementById(to!.url.hash.substring(1));
	// 	// // 	// TBD: consider opening a potential collapsed parent sections here
	// 	// // 	if (target) {
	// 	// // 		// const parentRect = scrollspyParent!.getBoundingClientRect();
	// 	// // 		const targetRect = target.getBoundingClientRect();
	// 	// // 		// This one prevents scrollspy dispatchEvent error on mount:
	// 	// // 		console.log('=== layout - afterNavigate - scroll to hash ===');
	// 	// // 		const targetScrollTop = scrollspyParent!.scrollTop + targetRect.top  + navBarBottom;
	// 	// // 		scrollspyParent!.scrollTop = targetScrollTop;
	// 	// // 		// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
	// 	// // 		scrollspyParent?.scrollTo({
	// 	// // 			left: scrollspyParent.scrollLeft,
	// 	// // 			top: scrollspyParent.scrollTop,
	// 	// // 			behavior: 'instant'
	// 	// // 		});
	// 	// // 	}
	// 	// // }
	// });

	// let windowElement: Window | null= $state(null);
	let navBar: HTMLElement | null = $state(null);
	let navBarBottom: number = $state(0);
	// let navBarBottomPrevious: number = $state(0);
	let contentArea: HTMLElement | null = $state(null);
	let contentAreaTop: number = $state(0);

	let contentAreaOffset: number = $state(0);
	// let scrollTarget = $derived(document.getElementById(page.url.hash.substring(1)) || contentArea);
	// let scrollTarget: number = $state(0);
	// let locationHash: string | null = $derived.by(() => {if(location && location.hash) {return location.hash } else { return null }});
	let locationHash: string | null = $state(null);

	// onMount(()=> {
	// 	windowElement = window;
	// })

	onMount(() => {
		// Reroute native history updates to SvelteKit to avoid router conflicts
		const originalPush = history.pushState.bind(history);
		const originalReplace = history.replaceState.bind(history);
		// Capture native prototype methods to bypass SvelteKit's patched wrappers
		const nativePush = History.prototype.pushState;
		const nativeReplace = History.prototype.replaceState;
		let bypassNativeOverride = false;
		history.pushState = (state: unknown, title: string, url?: string | URL | null) => {
			if (bypassNativeOverride) {
				// Call the native prototype directly to avoid warning wrappers
				return nativePush.call(history, state, title, url ?? '');
			}
			const nextUrl = url instanceof URL ? url.toString() : typeof url === 'string' ? url : null;
			if (nextUrl) {
				bypassNativeOverride = true;
				try {
					pushState(nextUrl, page.state);
				} finally {
					bypassNativeOverride = false;
				}
			} else {
				// Fallback to native method to avoid warnings
				nativePush.call(history, state, title, url ?? '');
			}
		};
		history.replaceState = (state: unknown, title: string, url?: string | URL | null) => {
			if (bypassNativeOverride) {
				// Call the native prototype directly to avoid warning wrappers
				return nativeReplace.call(history, state, title, url ?? '');
			}
			const nextUrl = url instanceof URL ? url.toString() : typeof url === 'string' ? url : null;
			if (nextUrl) {
				bypassNativeOverride = true;
				try {
					replaceState(nextUrl, page.state);
				} finally {
					bypassNativeOverride = false;
				}
			} else {
				// Fallback to native method to avoid warnings
				nativeReplace.call(history, state, title, url ?? '');
			}
		};

		return () => {
			history.pushState = originalPush;
			history.replaceState = originalReplace;
		};
	});

	afterNavigate(() => {
		console.log('=== layout - afterNavigate ===');
		// console.log({ href: page.url.href, pathname: page.url.pathname, hash: page.url.hash});
		locationHash = location.hash;
		navBarBottom =
			navBar && navBar.getBoundingClientRect().bottom > 0
				? navBar.getBoundingClientRect().bottom
				: 0;
		if (!locationHash) {
			// console.log('=== layout - afterNavigate - scroll to TOP ===');
			requestAnimationFrame(() => {
				scrollspyParent!.scrollTop = 0;
				// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
				scrollspyParent?.scrollTo({
					left: scrollspyParent.scrollLeft,
					top: scrollspyParent.scrollTop,
					behavior: 'smooth'
				});
			});
		} else {
			// console.log('=== layout - afterNavigate - scroll to hash ===');
			requestAnimationFrame(() => {
				scrollspyParent!.scrollTop -= navBarBottom;
				// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
				scrollspyParent?.scrollTo({
					left: scrollspyParent.scrollLeft,
					top: scrollspyParent.scrollTop,
					behavior: 'smooth'
				});
			});
		}
		// console.log('=== layout - afterNavigate - navBarBottom ===');
		// console.log(navBarBottom);
		// if (navBarBottom > 0 && window.innerWidth >= 640 ) {
		// 	console.log('=== layout - afterNavigate - scroll adjustment ===');
		// 	console.log('=== layout - afterNavigate - scrollspyParent!.scrollTop ===');
		// 	console.log(scrollspyParent!.scrollTop);
		// 	scrollspyParent!.scrollTop -= navBarBottom;
		// 	// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
		// 	scrollspyParent?.scrollTo({
		// 		left: scrollspyParent.scrollLeft,
		// 		top: scrollspyParent.scrollTop,
		// 		behavior: 'smooth'
		// 	});
		// }
		// if (locationHash) {
		// 	// console.log('=== layout - afterNavigate - scroll to hash ===');
		// 	const target = document.getElementById(locationHash);
		// 	// TBD: consider opening a potential collapsed parent sections here
		// 	if (target) {
		// 		const targetRect = target.getBoundingClientRect();
		// 		const parentRect = scrollspyParent!.getBoundingClientRect();
		// 		// This one prevents scrollspy dispatchEvent error on mount:
		// 		requestAnimationFrame(() => {
		// 			const targetScrollTop = targetRect.top - parentRect.top - navBarBottom -1000;
		// 			scrollspyParent!.scrollTop = targetScrollTop;
		// 			// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
		// 			scrollspyParent?.scrollTo({
		// 				left: scrollspyParent.scrollLeft,
		// 				top: scrollspyParent.scrollTop,
		// 				behavior: 'instant'
		// 			});
		// 		});
		// 	}
		// } else {
		// 	// console.log('=== layout - afterNavigate - scroll to TOP ===');
		// 	requestAnimationFrame(() => {
		// 		scrollspyParent!.scrollTop = -navBarBottom;
		// 		scrollspyParent!.scrollTo({
		// 			left: scrollspyParent!.scrollLeft,
		// 			top: scrollspyParent!.scrollTop,
		// 			behavior: 'smooth'
		// 		});
		// 	});
		// }
	});

	$effect(() => {
		console.log('=== layout - effect - tracking location.hash ===');
		console.log(locationHash);
		// console.log('=== layout - effect tracking page ===');
		// console.log({ href: page.url.href, pathname: page.url.pathname, hash: page.url.hash});
		// console.log('=== layout - effect - page ===');
		// console.log(page);
		// console.log('=== layout - effect - page.url.searchParams ===');
		// console.log(page.url.searchParams.get("page"));
		// console.log("=== layout - effect - pageStore ===");
		// console.log($pageStore.url.hash);
		// // console.log("=== layout - effect - window ===");
		// // console.log(windowElement?.onhashchange);
		// console.log('=== layout - effect - location ===');

		// console.log(location.hash);
	});

	const mainScrollEnd = (_event: Event) => {
		console.log('=== layout - onscrollend ===');
		// if (navBar) {
		// 	navBarBottom =
		// 		navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
		// }
		if (locationHash !== location.hash && window.innerWidth >= 640) {
			console.log('=== layout - onscrollend - location.hash changed ===');
			locationHash = location.hash;
			// console.log("=== layout - onscrollend - page ===");
			// console.log(page);
			// pushState(page.url.href, page);
			navBarBottom =
				navBar && navBar.getBoundingClientRect().bottom > 0
					? navBar.getBoundingClientRect().bottom
					: 0;
			requestAnimationFrame(() => {
				scrollspyParent!.scrollTop -= navBarBottom;
				// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
				scrollspyParent?.scrollTo({
					left: scrollspyParent.scrollLeft,
					top: scrollspyParent.scrollTop,
					behavior: 'smooth'
				});
			});
		}
		// const navBarBottomPrevious =
		// 	navBar && navBar.getBoundingClientRect().bottom > 0
		// 		? navBar.getBoundingClientRect().bottom
		// 		: 0;
		// // scrollTarget = page.url.hash
		// // 	? document.getElementById(page.url.hash.substring(1))?.getBoundingClientRect().top || 0
		// // 	: contentArea?.getBoundingClientRect().top || 0;
		// // TBD: add an "afterNavigate" here, so this is not trigggered on a user scroll action?
		// if (navBarBottomPrevious !== navBarBottom) {
		// 	console.log('=== layout - onscrollend - navBarBottom changed ===');
		// 	// const target = document.getElementById(page.url.hash.substring(1)) || contentArea;
		// 	// target?.scrollIntoView({ behavior: 'smooth', block: 'center' });
		// 	requestAnimationFrame(() => {
		// 		scrollspyParent!.scrollTop -= navBarBottom;
		// 		// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
		// 		scrollspyParent?.scrollTo({
		// 			left: scrollspyParent.scrollLeft,
		// 			top: scrollspyParent.scrollTop,
		// 			behavior: 'smooth'
		// 		});
		// 	});
		// }
		// // const targetRect = scrollTarget!.getBoundingClientRect();

		// // })
		// // const currentNavBarBottom = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
		// // if (navBarBottomPrevious !== currentNavBarBottom) {
		// // 	console.log('=== layout - effect - navBarBottom changed ===');
		// // }
		// navBarBottom =
		// 	navBar && navBar.getBoundingClientRect().bottom > 0
		// 		? navBar.getBoundingClientRect().bottom
		// 		: 0;
		contentAreaTop = contentArea ? contentArea.getBoundingClientRect().top : 0;
	};

	const mainAttachment: Attachment<HTMLElement> = (_node: HTMLElement) => {
		// console.log('=== layout - mainAttachment ===');
	};

	const contentAreaAttachment: Attachment<HTMLElement> = (_node: HTMLElement) => {
		// console.log('=== layout - contentAreaAttachment ===');
	};

	// $effect(() => {
	// 	console.log('=== layout - effect ===');
	// 	requestAnimationFrame(() => {
	// 		scrollspyParent!.scrollTop = scrollTarget;
	// 		// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
	// 		scrollspyParent?.scrollTo({
	// 			left: scrollspyParent.scrollLeft,
	// 			top: scrollspyParent.scrollTop,
	// 			behavior: 'smooth'
	// 		});
	// 	});
	// });

	// $effect(() => {
	// 	console.log('=== layout - effect ===');
	// 	if (navBarBottomPrevious !== navBarBottom) {
	// 		if (navBarBottomPrevious > 0 && navBarBottom === 0) {
	// 			console.log('=== layout - effect - navbar collapsed ===');
	// 			requestAnimationFrame(() => {
	// 				scrollspyParent!.scrollTop += navBarBottomPrevious;
	// 				scrollspyParent?.scrollTo({left: scrollspyParent.scrollLeft, top: scrollspyParent.scrollTop, behavior: 'instant' });
	// 			});
	// 		} else {
	// 			requestAnimationFrame(() => {
	// 				scrollspyParent!.scrollTop -= navBarBottomPrevious;
	// 				scrollspyParent?.scrollTo({
	// 					left: scrollspyParent.scrollLeft,
	// 					top: scrollspyParent.scrollTop,
	// 					behavior: 'instant'
	// 				});
	// 			});
	// 		}
	// 		navBarBottomPrevious = navBarBottom;
	// 	}
	// });

	// $effect(() =>  {
	// console.log('=== layout - effect  ===');

	// const navBarBottomPrevious = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
	// const scrollTarget = page.url.hash ? document.getElementById(page.url.hash.substring(1)) : contentArea;
	// const targetRect = scrollTarget!.getBoundingClientRect();
	// requestAnimationFrame(() => {
	// 	const targetScrollTop = targetRect.top;
	// 	scrollspyParent!.scrollTop = targetScrollTop;
	// 	// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
	// 	scrollspyParent?.scrollTo({
	// 		left: scrollspyParent.scrollLeft,
	// 		top: scrollspyParent.scrollTop,
	// 		behavior: 'smooth'
	// 	});
	// })
	// const currentNavBarBottom = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
	// if (navBarBottomPrevious !== currentNavBarBottom) {
	// 	console.log('=== layout - effect - navBarBottom changed ===');
	// }

	// // reset scrolling to zero, on internal navigation, if no hash is present:
	// if (!page.url.hash) {
	// 	console.log('=== layout - effect - scroll to TOP ===');
	// 	scrollspyParent!.scrollTop = 0;
	// 	scrollspyParent!.scrollTo({
	// 		left: scrollspyParent!.scrollLeft,
	// 		top: scrollspyParent!.scrollTop,
	// 		behavior: 'smooth'
	// 	});
	// }
	// else{
	// 	console.log('=== layout - effect - scroll to HASH ===');
	// 	const target = document.getElementById(page.url.hash.substring(1));
	// 	// TBD: consider opening a potential collapsed parent sections here
	// 	// const navBarBottomPrevious = $state.snapshot(navBarBottom);
	// 	const navBarBottomPrevious = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
	// 	if (target) {
	// 		const targetRect = target.getBoundingClientRect();
	// 		// This one prevents scrollspy dispatchEvent error on mount:
	// 		requestAnimationFrame(() => {
	// 			const targetScrollTop = targetRect.top;
	// 			scrollspyParent!.scrollTop = targetScrollTop;
	// 			// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
	// 			scrollspyParent?.scrollTo({
	// 				left: scrollspyParent.scrollLeft,
	// 				top: scrollspyParent.scrollTop,
	// 				behavior: 'smooth'
	// 			});
	// 		})
	// 	}
	// 	const currentNavBarBottom = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
	// 	if (navBarBottomPrevious !== currentNavBarBottom) {
	// 		console.log('=== layout - effect - navBarBottom changed ===');
	// 		// if (navBarBottomPrevious > 0 && currentNavBarBottom === 0) {
	// 		// 	console.log('=== layout - effect - navbar collapsed ===');
	// 		// 	requestAnimationFrame(() => {
	// 		// 		scrollspyParent!.scrollTop += currentNavBarBottom;
	// 		// 		scrollspyParent?.scrollTo({left: scrollspyParent.scrollLeft, top: scrollspyParent.scrollTop, behavior: 'instant' });
	// 		// 	});
	// 		// } else {
	// 		// 	requestAnimationFrame(() => {
	// 		// 		scrollspyParent!.scrollTop -= currentNavBarBottom;
	// 		// 		scrollspyParent?.scrollTo({
	// 		// 			left: scrollspyParent.scrollLeft,
	// 		// 			top: scrollspyParent.scrollTop,
	// 		// 			behavior: 'instant'
	// 		// 		});
	// 		// 	});
	// 		// }
	// 	// 	navBarBottomPrevious = navBarBottom;
	// 	}
	// }
	// })

	// TBD: could this be an attachemnt to main instead?
	onMount(() => {
		console.log('=== layout - onMount ===');
		locationHash = location.hash ? location.hash : null;
		// navBarBottom = navBar && navBar.getBoundingClientRect().bottom > 0 ? navBar.getBoundingClientRect().bottom : 0;
		// contentAreaTop = contentArea ? contentArea.getBoundingClientRect().top : 0;
		// contentAreaOffset = contentAreaTop - navBarBottom;
		// adjustContentAreaOffset();

		// TBD: change into scrollTo with behavior instant?
		// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));

		// Scrolling triggered by server changes, potential server side navigation (redirect?) and initial hash handling:
		// for now just trigger a afterNavigate manually:
		// goto(page.url, { replaceState: true, noScroll: true, state: page.state });

		// that one looked good:
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
				// This one prevents scrollspy dispatchEvent error on mount:
				// const targetScrollTop = scrollspyParent!.scrollTop + targetRect.top - parentRect.top;
				scrollspyParent!.scrollTop += targetRect.top - parentRect.top;
				// scrollspyParent!.dispatchEvent(new Event('scroll', { bubbles: true }));
				scrollspyParent?.scrollTo({
					left: scrollspyParent.scrollLeft,
					top: scrollspyParent.scrollTop,
					behavior: 'smooth'
				});
			}
		}
	});
</script>

<!-- <svelte:window onhashchange={() => console.log("hash changed")} /> -->

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

<!-- style:scroll-padding-top={`${navBarBottom}pt`} -->
<main
	bind:this={scrollspyParent}
	id="scrollspy-scrollable-parent"
	class="h-screen w-screen overflow-x-scroll overflow-y-auto"
	onscrollend={mainScrollEnd}
	{@attach mainAttachment}
>
	<WelcomeModal
		bind:session={data.session}
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
				{#each sidebarLinks as mainItem (mainItem.id)}
					<SidebarItem
						content={{ ...mainItem, pathname: mainItem.pathname || page.url.pathname }}
						topLevel={true}
						topoffset={navBarBottom}
					/>
					<!-- topoffset={internalNavigationTarget} -->
					<!-- topoffset={navBarBottom} -->
					<!-- topoffset={`[--scrollspy-offset:${navBarBottom + 8}]`} -->
				{/each}
			</ul>
		</div>
		NavBarBottom: {navBarBottom}
		<br />
		ContentAreaTop: {contentAreaTop}
		<br />
		ContentAreaOffset: {contentAreaOffset}
		<br />
		Pathname: {page.url.pathname}
		<br />
		Hash: {page.url.hash}
	</aside>
	<!-- style="--nav-offset: {navBarBottom}px" -->
	<!-- style:scroll-padding-top={`${navBarBottom}px`} -->
	<!-- onscrollend={adjustScrollForStickyNavbar} -->
	<div class="bg-base-100 xs:mx-5 xs:mt-5 mt-2 w-screen px-2 sm:h-full" use:applyTheming>
		<!-- TBD: put navbar into component -->
		<!-- <div class="h-full"> -->
		<nav
			class="navbar rounded-box bg-base-200 shadow-shadow border-outline-variant sticky start-0 top-0 z-1 flex justify-between border-1 border-b shadow-md max-sm:h-14 max-sm:px-3 md:items-center"
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
					<!-- {#if !loggedIn}
						<button
							class="btn btn-neutral shadow-neutral ml-2 rounded-full shadow-sm"
							aria-label="Log In"
						>
							<a href="/login">Log in</a>
						</button>
					{:else}
						<button
							class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
							aria-label="Log Out"
						>
							<a href="/logout">Log out</a>
						</button>
					{/if} -->
				</div>
			</div>
		</nav>
		<!-- </div> -->

		<!-- <aside
			id="collapsible-mini-sidebar"
			class="overlay [--auto-close:sm] sm:shadow-none overlay-open:translate-x-0 drawer drawer-start hidden max-w-64  sm:flex sm:translate-x-0 pt-16"
			tabindex="-1"
		>
			<div class="drawer-body px-2 pt-4">
				<ul class="menu p-0">
				<li>
					<a href="#top">
					<span class="icon-[tabler--home] size-5"></span>
					Home
					</a>
				</li>
				<li>
					<a href="/playground/page3#loreum1">
					<span class="icon-[tabler--user] size-5"></span>
					Page 3 - Loreum 1
					</a>
				</li>
				<li>
					<a href="/playground/page3#loreum2">
					<span class="icon-[tabler--message] size-5"></span>
					Page 3 - Loreum 2
					</a>
				</li>
				</ul>
			</div>
		</aside> -->

		<div
			id="scrollspy"
			class="sm:overlay-minified:ps-19 overlay-open:ps-0 space-y-4 pt-2 transition-all duration-300 sm:mx-2 sm:mt-2 sm:ps-66"
			bind:this={contentArea}
			{@attach contentAreaAttachment}
		>
			{@render children?.()}
		</div>
	</div>
</main>

<!-- style:padding-top={`${contentAreaOffset + 2}pt`} -->
<!-- style:scroll-margin-top="150pt" -->
<!-- style:padding-top={`${contentAreaOffset + 2}pt`} -->
<!-- style="--nav-offset: {navBarBottom}px"
<style>
	:global(#scrollspy [id]) {
		scroll-margin-top: var(--nav-offset, 0px);
	}
</style> -->
