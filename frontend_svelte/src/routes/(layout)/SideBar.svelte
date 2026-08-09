<script lang="ts">
	import { scrollY } from 'svelte/reactivity/window';

	import { page } from '$app/state';
	import Guard from '$components/Guard.svelte';
	import {
		getDebugSidebarLinks,
		getProtectedSidebarLinks,
		getSidebarLinks,
		page6Content
	} from '$lib/contexts/sidebar.svelte';
	import { initOverlay } from '$lib/userInterface';

	import LoginOutButton from './LoginOutButton.svelte';
	import Logo from './Logo.svelte';
	import SidebarItem from './SidebarItem.svelte';
	import SidebarToggleButton from './SideBarToggleButton.svelte';

	let {
		loggedIn,
		parentUrl,
		debug = $bindable(),
		navBarBottom
	}: {
		loggedIn: boolean;
		parentUrl: string | undefined;
		debug: boolean;
		navBarBottom: number;
	} = $props();

	// TBD: put sidebarLinks in a store and bind it here instead of passing it down as a prop!
	// let sidebarLinks: SidebarItemContent[] = $state([
	// 	{
	// 		name: 'Docs',
	// 		pathname: resolve('/(plain)/docs'),
	// 		icon: 'icon-[oui--documentation]',
	// 		id: 'docs',
	// 		items: []
	// 	},
	// 	{
	// 		name: 'Open Playground',
	// 		pathname: resolve('/(layout)/playground'),
	// 		icon: 'icon-[mdi--playground-seesaw]',
	// 		id: 'playground',
	// 		items: [
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
	// 						hash: '#building-blocks',
	// 						id: 'building-blocks',
	// 						items: [
	// 							{
	// 								name: 'Shadcn-svelte',
	// 								icon: 'icon-[bxl--shadcn-ui]',
	// 								pathname: resolve('/(layout)/playground/design/shadcn'),
	// 								id: 'shadcn'
	// 							},
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
	// 		name: 'Protected Data',
	// 		pathname: resolve('/(layout)/(protected)/protected'),
	// 		icon: 'icon-[mingcute--lock-fill]',
	// 		id: 'dashboard',
	// 		items: [
	// 			{
	// 				name: 'Demo Resources',
	// 				pathname: resolve('/(layout)/(protected)/backend-demo-resource'),
	// 				icon: 'icon-[grommet-icons--resources]',
	// 				id: 'demo-resource',
	// 				items: [
	// 					{
	// 						name: 'Rest API',
	// 						pathname: resolve('/(layout)/(protected)/backend-demo-resource/restapi'),
	// 						icon: 'icon-[dashicons--rest-api]',
	// 						id: 'demo-resource-restapi'
	// 					},
	// 					{
	// 						name: 'Socket IO',
	// 						pathname: resolve('/(layout)/(protected)/backend-demo-resource/socketio'),
	// 						icon: 'icon-[tabler--brand-socket-io]',
	// 						id: 'demo-resource-socketio'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				name: 'Presentations',
	// 				pathname: resolve('/(layout)/presentation/(protected)/setup'),
	// 				icon: 'icon-[fa6-solid--chalkboard]',
	// 				id: 'presentations'
	// 			},
	// 			{
	// 				name: 'Questions',
	// 				pathname: resolve('/(layout)/question/(protected)/setup'),
	// 				icon: 'icon-[codicon--question]',
	// 				id: 'questions'
	// 			},
	// 			{
	// 				name: 'Hierarchical Resources',
	// 				pathname: resolve('/(layout)/(protected)/backend-protected-hierarchy'),
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
	// 						pathname: resolve('/(layout)/(protected)/identities'),
	// 						icon: 'icon-[mdi--account-multiple-outline]',
	// 						id: 'identities-all'
	// 					},
	// 					{
	// 						name: 'Microsoft',
	// 						pathname: resolve('/(layout)/(protected)/msgraph'),
	// 						icon: 'icon-[fluent--person-20-filled]',
	// 						id: 'identities-microsoft'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				name: 'Socket.IO',
	// 				pathname: resolve('/(layout)/(protected)/socketio'),
	// 				icon: 'icon-[tabler--brand-socket-io]',
	// 				id: 'socketio'
	// 			},
	// 			{
	// 				name: 'Session Data',
	// 				pathname: resolve('/(layout)/(protected)/sessiondata'),
	// 				icon: 'icon-[solar--hashtag-circle-linear]',
	// 				id: 'sessiondata'
	// 			}
	// 		]
	// 	}
	// ]);

	// let debugSidebarLinks: SidebarItemContent[] = $state([
	// 	{
	// 		name: 'Page 1',
	// 		pathname: resolve('/(layout)/playground/page1'),
	// 		icon: 'icon-[tabler--user]',
	// 		id: 'page1',
	// 		items: []
	// 	},
	// 	{
	// 		name: 'Page 2',
	// 		pathname: resolve('/(layout)/playground/page2'),
	// 		icon: 'icon-[icon-park-outline--page]',
	// 		id: 'page2',
	// 		items: [
	// 			{
	// 				id: 'page2-loreum1',
	// 				name: 'Loreum 1',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg2loreum1'
	// 			},
	// 			{
	// 				id: 'page2-loreum2',
	// 				name: 'Loreum 2',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg2loreum2'
	// 			},
	// 			{
	// 				name: 'Sub category',
	// 				icon: 'icon-[material-symbols--folder-outline-rounded]',
	// 				hash: '#pg2sub-category',
	// 				id: 'page2-sub-category',
	// 				items: [
	// 					{
	// 						id: 'page2-loreum3',
	// 						name: 'Loreum 3',
	// 						icon: 'icon-[mdi--text]',
	// 						hash: '#pg2loreum3'
	// 					},
	// 					{
	// 						id: 'page2-loreum4',
	// 						name: 'Loreum 4',
	// 						icon: 'icon-[mdi--text]',
	// 						hash: '#pg2loreum4'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				id: 'page2-loreum5',
	// 				name: 'Loreum 5',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg2loreum5'
	// 			},
	// 			{
	// 				id: 'page2-loreum6',
	// 				name: 'Loreum 6',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg2loreum6'
	// 			}
	// 		]
	// 	},
	// 	{
	// 		name: 'Page 3',
	// 		pathname: resolve('/(layout)/playground/page3'),
	// 		icon: 'icon-[icon-park-outline--page]',
	// 		id: 'page3',
	// 		items: [
	// 			{
	// 				id: 'page3-loreum1',
	// 				name: 'Loreum 1',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg3loreum1'
	// 			},
	// 			{
	// 				id: 'page3-loreum2',
	// 				name: 'Loreum 2',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg3loreum2'
	// 			},
	// 			{
	// 				id: 'page3-loreum2a',
	// 				name: 'Loreum 2a',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg3loreum2a'
	// 			},
	// 			{
	// 				name: 'Sub category',
	// 				icon: 'icon-[material-symbols--folder-outline-rounded]',
	// 				hash: '#pg3sub-category',
	// 				id: 'pg3sub-category',
	// 				items: [
	// 					{
	// 						id: 'page3-loreum3p1',
	// 						name: 'Loreum 3.1',
	// 						icon: 'icon-[mdi--text]',
	// 						hash: '#pg3loreum3p1'
	// 					},
	// 					{
	// 						id: 'page3-loreum3p2',
	// 						name: 'Loreum 3.2',
	// 						icon: 'icon-[mdi--text]',
	// 						hash: '#pg3loreum3p2'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				id: 'page3-loreum4',
	// 				name: 'Loreum 4',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg3loreum4'
	// 			},
	// 			{
	// 				id: 'page3-loreum5',
	// 				name: 'Loreum 5',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#pg3loreum5'
	// 			}
	// 		]
	// 	},
	// 	{
	// 		id: 'further-page',
	// 		name: 'Further Page',
	// 		pathname: resolve('/(layout)/playground/page4'),
	// 		icon: 'icon-[tabler--mail]',
	// 		items: [
	// 			{
	// 				id: 'page4-loreum1',
	// 				name: 'Loreum 1',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#loreum1'
	// 			},
	// 			{
	// 				id: 'page4-loreum2',
	// 				name: 'Loreum 2',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#loreum2'
	// 			},
	// 			{
	// 				name: 'Sub category',
	// 				icon: 'icon-[material-symbols--folder-outline-rounded]',
	// 				hash: '#sub-category-page4',
	// 				id: 'page4-sub-category',
	// 				items: [
	// 					{
	// 						id: 'page4-loreum3',
	// 						name: 'Loreum 3',
	// 						icon: 'icon-[mdi--text]',
	// 						hash: '#loreum3'
	// 					},
	// 					{
	// 						id: 'page4-loreum4',
	// 						name: 'Loreum 4',
	// 						icon: 'icon-[mdi--text]',
	// 						hash: '#loreum4'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				id: 'page4-sub-pages-section',
	// 				name: 'Sub-pages',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#page4-sub-pages-section'
	// 			},
	// 			{
	// 				name: 'Sub-page 4.1',
	// 				icon: 'icon-[mingcute--directory-line]',
	// 				pathname: resolve('/(layout)/playground/page4/page4-1'),
	// 				id: 'page4p1',
	// 				items: [
	// 					{
	// 						id: 'page4p1-loreum1',
	// 						name: 'Loreum 1 pg4.1',
	// 						icon: 'icon-[mdi--text]',
	// 						pathname: resolve('/(layout)/playground/page4/page4-1'),
	// 						hash: '#loreum1'
	// 					},
	// 					{
	// 						id: 'page4p1-loreum2',
	// 						name: 'Loreum 2 pg4.2',
	// 						icon: 'icon-[mdi--text]',
	// 						pathname: resolve('/(layout)/playground/page4/page4-1'),
	// 						hash: '#loreum2'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				name: 'Sub-page 4.2',
	// 				icon: 'icon-[material-symbols--folder-outline-rounded]',
	// 				pathname: resolve('/(layout)/playground/page4/page4-2'),
	// 				id: 'page4p2',
	// 				items: [
	// 					{
	// 						id: 'page4p2-loreum1',
	// 						name: 'Loreum 1 pg4.2',
	// 						icon: 'icon-[mdi--text]',
	// 						pathname: resolve('/(layout)/playground/page4/page4-2'),
	// 						hash: '#loreum1'
	// 					},
	// 					{
	// 						id: 'page4p2-loreum2',
	// 						name: 'Loreum 2 pg4.2',
	// 						icon: 'icon-[mdi--text]',
	// 						pathname: resolve('/(layout)/playground/page4/page4-2'),
	// 						hash: '#loreum2'
	// 					}
	// 				]
	// 			},
	// 			{
	// 				id: 'page4-loreum6',
	// 				name: 'Loreum 6',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#loreum6'
	// 			}
	// 		]
	// 	},
	// 	{
	// 		name: 'Page 5',
	// 		pathname: resolve('/(layout)/playground/page5'),
	// 		icon: 'icon-[tabler--user]',
	// 		id: 'page5',
	// 		items: [
	// 			{
	// 				id: 'page5-loreum1',
	// 				name: 'Loreum 1',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#loreum1'
	// 			},
	// 			{
	// 				id: 'page5-loreum2',
	// 				name: 'Loreum 2',
	// 				icon: 'icon-[mdi--text]',
	// 				hash: '#loreum2'
	// 			}
	// 		]
	// 	}
	// ]);

	// const sidebarLinksAccessor = getSidebarLinks();
	// const protectedSidebarLinksAccessor = getProtectedSidebarLinks();
	// const debugSidebarLinksAccessor = getDebugSidebarLinks();

	const sidebarLinks = getSidebarLinks();
	const protectedSidebarLinks = getProtectedSidebarLinks();
	const debugSidebarLinks = getDebugSidebarLinks();

	const PAGE6_ID = 'page6';
	const hasPage6 = $derived(debugSidebarLinks.some((item) => item.id === PAGE6_ID));

	const toggleDebugPage6 = () => {
		// const currentDebugLinks = getDebugSidebarLinks();
		const existingIndex = debugSidebarLinks.findIndex((item) => item.id === PAGE6_ID);
		if (existingIndex >= 0) {
			debugSidebarLinks.splice(existingIndex, 1);
			return;
		}
		debugSidebarLinks.push(...page6Content);
	};
</script>

{#snippet sidebarPartItem(href: string, icon: string, text: string, listItemClasses?: string)}
	<li class="text-primary {listItemClasses}">
		<a {href}>
			<span class="{icon} size-5"></span>
			<span class="overlay-minified:hidden">{text}</span>
		</a>
	</li>
{/snippet}

<aside
	id="collapsible-mini-sidebar"
	class="overlay overlay-minified:w-19 overlay-open:translate-x-0 drawer drawer-start bg-base-150 border-base-content/20 start-0 top-0 hidden w-66 border-e [--auto-close:sm] sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
	tabindex="-1"
	{@attach initOverlay}
>
	<div class="mx-7 flex h-24 flex-row items-center justify-between md:h-26">
		<div class="hidden sm:block">
			<SidebarToggleButton
				extraClasses="hidden sm:flex"
				overlayModifier={{ 'data-overlay-minifier': '#collapsible-mini-sidebar' }}
			/>
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
					<LoginOutButton {loggedIn} {parentUrl} />
				</div>
			</li>
		</ul>
		<div class="divider"></div>
		<ul class="menu p-0">
			<!-- TBD: add a toggle between "app navigation" and "on this page" -->
			{#each sidebarLinks as sidebarItem (sidebarItem.id)}
				<!-- TBD: remove topoffset -->
				<SidebarItem
					content={{ ...sidebarItem, pathname: sidebarItem.pathname || page.url.pathname }}
					topLevel={true}
				/>
				<!-- {scrollspyParent} -->
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
					/>
					<!-- {scrollspyParent} -->
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
					/>
					<!-- {scrollspyParent} -->
					<!-- topoffset={navBarBottom} -->
				{/each}
			{/if}
		</ul>
	</div>
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
		<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
	</div>

	{#if debug}
		<button
			class="btn btn-primary btn-gradient max-sm:btn-circle max-sm:ml-2 md:rounded-full"
			onclick={toggleDebugPage6}
		>
			{#if !hasPage6}
				<span class="icon-[tabler--plus] size-5"></span>
				<div class="hidden md:block">add page 6</div>
			{:else}
				<span class="icon-[tabler--minus] size-5"></span>
				<div class="hidden md:block">remove page 6</div>
			{/if}
		</button>
		scrollY: {scrollY.current}
		<br />
		navBarBottom: {navBarBottom}
	{/if}
	<!-- {navBarBottom}
		<br />
		{locationPageAndHash?.page}{locationPageAndHash?.hash}
		<br /> -->
</aside>
