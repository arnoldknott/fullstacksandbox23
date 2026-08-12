import { createContext } from 'svelte';

import { resolve } from '$app/paths';
import type { SidebarItemContent } from '$lib/types';

// only pre-assign global context keys for app-wide and data-independent links,
// and mutate later as needed, e.g. for user-specific links

export const initialSidebarLinks: SidebarItemContent[] = $state([
	{
		name: 'Docs',
		pathname: resolve('/(plain)/docs'),
		icon: 'icon-[oui--documentation]',
		id: 'docs',
		items: []
	},
	{
		name: 'Open Playground',
		pathname: resolve('/(layout)/playground'),
		icon: 'icon-[mdi--playground-seesaw]',
		id: 'playground',
		items: [
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
						hash: '#building-blocks',
						id: 'building-blocks',
						items: [
							{
								name: 'Shadcn-svelte',
								icon: 'icon-[bxl--shadcn-ui]',
								pathname: resolve('/(layout)/playground/design/shadcn'),
								id: 'shadcn'
							},
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

export const initialProtectedSidebarLinks: SidebarItemContent[] = $state([
	{
		name: 'Protected Data',
		pathname: resolve('/(layout)/(protected)/protected'),
		icon: 'icon-[mingcute--lock-fill]',
		id: 'dashboard',
		items: [
			{
				name: 'Demo Resources',
				pathname: resolve('/(layout)/(protected)/backend-demo-resource'),
				icon: 'icon-[grommet-icons--resources]',
				id: 'demo-resource',
				items: [
					{
						name: 'Rest API',
						pathname: resolve('/(layout)/(protected)/backend-demo-resource/restapi'),
						icon: 'icon-[dashicons--rest-api]',
						id: 'demo-resource-restapi'
					},
					{
						name: 'Socket IO',
						pathname: resolve('/(layout)/(protected)/backend-demo-resource/socketio'),
						icon: 'icon-[tabler--brand-socket-io]',
						id: 'demo-resource-socketio'
					}
				]
			},
			{
				name: 'Presentations',
				pathname: resolve('/(layout)/presentation/(protected)/setup'),
				icon: 'icon-[fa6-solid--chalkboard]',
				id: 'presentations'
			},
			{
				name: 'Questions',
				pathname: resolve('/(layout)/question/(protected)/setup'),
				icon: 'icon-[codicon--question]',
				id: 'questions'
			},
			{
				name: 'Hierarchical Resources',
				pathname: resolve('/(layout)/(protected)/backend-protected-hierarchy'),
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
						pathname: resolve('/(layout)/(protected)/identities'),
						icon: 'icon-[mdi--account-multiple-outline]',
						id: 'identities-all'
					},
					{
						name: 'Microsoft',
						pathname: resolve('/(layout)/(protected)/msgraph'),
						icon: 'icon-[fluent--person-20-filled]',
						id: 'identities-microsoft'
					}
				]
			},
			{
				name: 'Socket.IO',
				pathname: resolve('/(layout)/(protected)/socketio'),
				icon: 'icon-[tabler--brand-socket-io]',
				id: 'socketio'
			},
			{
				name: 'Session Data',
				pathname: resolve('/(layout)/(protected)/sessiondata'),
				icon: 'icon-[solar--hashtag-circle-linear]',
				id: 'sessiondata'
			}
		]
	}
]);

export const initialDebugSidebarLinks: SidebarItemContent[] = $state([
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

export const page6Content = $state([
	{
		name: 'Page 6',
		pathname: resolve('/(layout)/playground/user-interface/sidebar/recursion/page6'),
		icon: 'icon-[solar--structure-linear]',
		id: 'page6',
		items: [
			{
				id: 'page6-loreum1',
				name: 'Loreum 1',
				icon: 'icon-[mdi--text]',
				hash: '#loreum1'
			},
			{
				id: 'page6-loreum2',
				name: 'Loreum 2',
				icon: 'icon-[fe--picture]',
				hash: '#loreum2'
			},
			{
				name: 'Sub category',
				icon: 'icon-[material-symbols--folder-outline-rounded]',
				hash: '#sub-category',
				id: 'page6-sub-category',
				items: [
					{
						id: 'page6-loreum3',
						name: 'Loreum 3',
						icon: 'icon-[mdi--text]',
						hash: '#loreum3'
					},
					{
						id: 'page6-loreum4',
						name: 'Loreum 4',
						icon: 'icon-[fluent--document-24-regular]',
						hash: '#loreum4'
					}
				]
			},
			{
				id: 'page6-loreum5',
				name: 'Loreum 5',
				icon: 'icon-[fe--picture]',
				hash: '#loreum5'
			},
			{
				id: 'page6-loreum6',
				name: 'Loreum 6',
				icon: 'icon-[fe--picture]',
				hash: '#loreum6'
			}
		]
	}
]);

export const [getSidebarLinks, setSidebarLinks] = createContext<SidebarItemContent[]>();
export const [getProtectedSidebarLinks, setProtectedSidebarLinks] =
	createContext<SidebarItemContent[]>();
export const [getDebugSidebarLinks, setDebugSidebarLinks] = createContext<SidebarItemContent[]>();
export const [getOnThisPageLinks, setOnThisPageLinks] = createContext<SidebarItemContent[]>();
