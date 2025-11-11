<script lang="ts">
	import { themeStore } from '$lib/stores';
	import type { AppTheme } from '$lib/theming';
	import { Hct, hexFromArgb } from '@material/material-color-utilities';
	import { onDestroy } from 'svelte';
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import NavigationCard from '$components/NavigationCard.svelte';
	// import type { Attachment } from 'svelte/attachments';
	// import { afterNavigate } from '$app/navigation';
	import Card from '$components/Card.svelte';
	import { Variant, type ColorConfig } from '$lib/theming';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { enhance } from '$app/forms';
	import ShareItem from './ShareItem.svelte';
	// import type { PageProps } from '../$types';
	import { page } from '$app/state';
	import type { ActionResult } from '@sveltejs/kit';
	import {
		initDropdown,
		initOverlay,
		initCarousel,
		initTabs,
		initTooltip
	} from '$lib/userInterface';
	import { Action, AccessHandler, IdentityType } from '$lib/accessHandler';
	import type { AccessShareOption } from '$lib/types';
	import ThemePicker from './ThemePicker.svelte';
	import ArtificialIntelligencePicker from './ArtificialIntelligencePicker.svelte';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
	import Panes, { type PaneData } from './Panes.svelte';
	// import Panes from './Panes.svelte';
	// import JsonData from '$components/JsonData.svelte';

	let prod = $state(page.url.searchParams.get('prod') === 'false' ? false : true);
	let develop = $state(page.url.searchParams.get('develop') === 'true' ? true : false);

	// data for card with navigation in title:
	const cardsNavigation = [
		{
			title: "Here's a title",
			description:
				'Some test text, here. Can go over several lines. And if it does, the cards in the same line will adjust to the longest card. This is a good way to keep the layout clean and consistent.',
			link: '#top'
		},
		{
			title: 'One more title',
			description: 'Some shorter text here - but adjusts to the height of the neighbor card',
			link: '#top'
		},
		{
			title: 'A third title',
			description:
				'This one is meant to fill the row. Note how the cards are responsive on smaller screens.',
			link: '#top'
		}
	];

	// for dropdown menus:
	let actionButtonShareMenu: HTMLElement;
	let dropdownShareDropdown: HTMLElement;
	let dropdownMenu: HTMLElement;
	let dropdownShare: HTMLElement;

	// // TBD: is this stopping the dropdown from stalling? No, it doesn't, but the issue only exists in development mode.
	// window.HSStaticMethods.autoInit(["dropdown"]);

	// TBD: make sure all dropdowns close and get reset, when user does not click any of the list items, but elsewhere on the screen.
	// use the event from the main dropdown to listen and close the child dropdowns.
	// const closeChildDropdowns: Attachment = () => {
	// 	dropdownMenu?.on("close", dropdownShareDropdown?.close());
	// TBD: potentially using {@attach} for this?

	// data for share menu:
	const shareOptions: AccessShareOption[] = $state(
		[
			{
				identity_id: '1',
				identity_name: 'The A Team',
				identity_type: IdentityType.MICROSOFT_TEAM,
				action: Action.READ
			},
			{
				identity_id: '2',
				identity_name: 'Awesome Team',
				identity_type: IdentityType.MICROSOFT_TEAM,
				action: Action.WRITE
			},
			{
				identity_id: '3',
				identity_name: 'Ueber Group',
				identity_type: IdentityType.UEBER_GROUP,
				action: undefined
			},
			{
				identity_id: '4',
				identity_name: 'Group some group',
				identity_type: IdentityType.GROUP,
				action: Action.OWN
			},
			{
				identity_id: '5',
				identity_name: 'Sub Group',
				identity_type: IdentityType.SUB_GROUP,
				action: Action.READ
			},
			{
				identity_id: '6',
				identity_name: 'Sub-Sub-Group',
				identity_type: IdentityType.SUB_SUB_GROUP,
				action: Action.OWN
			},
			{
				identity_id: '7',
				identity_name: 'Tom User',
				identity_type: IdentityType.USER,
				action: Action.READ
			},
			{
				identity_id: '8',
				identity_name: 'Another user with a very long Team Name of ',
				identity_type: IdentityType.USER,
				action: Action.WRITE
			}
		].sort(
			(a, b) => a.identity_type - b.identity_type || a.identity_name.localeCompare(b.identity_name)
		)
	);

	// selections
	let browser = $derived.by(() => {
		if (typeof navigator !== 'undefined') {
			const userAgent = navigator.userAgent;
			if (userAgent.includes('Chrome')) {
				return 'Chrome';
			} else if (userAgent.includes('Firefox')) {
				return 'Firefox';
			} else if (userAgent.includes('Safari')) {
				return 'Safari';
			} else if (userAgent.includes('Edge')) {
				return 'Edge';
			} else {
				return 'Other';
			}
		}
		return 'Unknown';
	});

	let selectionFocused = $state(false);
	let share = $state(false);
	let selectedAction = $state(shareOptions[1].action);

	const desiredActions = (selectedAction?: Action) => {
		let action = shareOptions[1].action;
		let newAction = undefined;
		// deleting access policy:
		if (selectedAction === undefined && action) {
			action = undefined;
			newAction = undefined;
		}
		// creating a new access policy:
		else if (shareOptions[1].action === undefined) {
			action = selectedAction;
		}
		// updating an existing access policy:
		// else if (selectedAction && shareOption.action !== selectedAction) {
		else {
			newAction = selectedAction;
		}
		// console.log(
		// 	'=== shareItem - desiredActions - Values for access policy ===',
		// 	shareOption.action,
		// 	selectedAction
		// );
		return {
			action: action,
			new_action: newAction
		};
	};

	const handleRightsChangeResponse = async (result: ActionResult, update: () => void) => {
		if (result.type === 'success') {
			const identity = shareOptions.find(
				(option) => option.identity_id === result.data?.identityId
			);
			if (identity) {
				identity.action = result.data?.confirmedNewAction
					? (result.data.confirmedNewAction.toString() as Action)
					: undefined;
			}
		} else {
			// handle error: show error message
		}
		update();
	};

	// for status sliders:
	let theme = $state({} as AppTheme);
	const unsbscribeThemeStore = themeStore.subscribe((value) => {
		theme = value;
	});

	// for HCT:
	// red: hue = 25,
	// (yellow: hue = 104,)
	// green: hue = 130
	// use chroma and tone from error container - always keeps the color!
	// text on it:
	// chorma and tone always from "on error container"
	let errorHct = $derived.by(() => {
		if (!theme.currentMode) {
			return Hct.from(25, 80, 30);
		} else {
			return Hct.fromInt(theme[theme.currentMode].colors['error']);
		}
	});
	let onErrorHct = $derived.by(() => {
		if (!theme.currentMode) {
			return Hct.from(24, 13, 90);
		} else {
			return Hct.fromInt(theme[theme.currentMode].colors['onError']);
		}
	});
	let status = $state([50, 0, 100]);
	let statusColorsHue = $derived(
		status.map((s) => ({
			background: s * 1.05 + 25,
			text: s * 1.05 + 25
		}))
	);
	let statusColors = $derived(
		statusColorsHue.map((hue) => ({
			background: hexFromArgb(Hct.from(hue.background, errorHct.chroma, errorHct.tone).toInt()),
			text: hexFromArgb(Hct.from(hue.background, onErrorHct.chroma, onErrorHct.tone).toInt())
		}))
	);
	onDestroy(() => {
		unsbscribeThemeStore();
	});

	// for edit button:
	let edit = $state(false);

	// for artificial intelligence settings:
	let artificialIntelligenceConfiguration: ArtificialIntelligenceConfig = $state({
		enabled: true,
		model: Model.MODEL1,
		temperature: 0.7
		// max_tokens: 2048
	});

	let artificialIntelligenceForm = $state<HTMLFormElement | null>(null);

	// for theme picker:
	let themeConfiguration: ColorConfig = $state({
		sourceColor: '#769CDF',
		variant: Variant.TONAL_SPOT,
		contrast: 0.0
	});
	let sourceColor = $derived(themeConfiguration.sourceColor);
	let variant = $derived(themeConfiguration.variant);
	let contrast = $derived(themeConfiguration.contrast);
	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
	const allContrasts = Array.from(
		{ length: (contrastMax - contrastMin) / contrastStep + 1 },
		(_, i) => contrastMin + i * contrastStep
	);

	let mode = $state<'light' | 'dark'>('light');

	let themeForm = $state<HTMLFormElement | null>(null);

	// shared for artificial intelligence and theme picker:
	const saveProfileAccount = async () => {
		// if (page.data.session?.loggedIn) {
		themeForm?.requestSubmit();
		console.log('=== layout - saveProfileAccount - themeConfiguration ===');
		console.log($state.snapshot(themeConfiguration));
		// }
	};

	const updateProfileAccount: SubmitFunction = async () => {
		return () => {};
	};

	// for diff component:
	let diffWidth: number = $state(0);
	let firstDiffWidth: number = $state(0);
	let secondDiffWidth: number = $state(0);
	let resizerDiff: HTMLDivElement | null = $state(null);

	let diffWidthAdoptiveFlex: number = $state(0);
	let secondDiffWidthAdoptiveFlex: number = $state(0);
	let firstDiffWidthAdoptiveFlex = $derived(diffWidthAdoptiveFlex - secondDiffWidthAdoptiveFlex);

	let diffWidthAdoptiveGrid: number = $state(0);
	let secondDiffWidthAdoptiveGrid: number = $state(0);
	let firstDiffWidthAdoptiveGrid = $derived(diffWidthAdoptiveGrid - secondDiffWidthAdoptiveGrid);

	// for panes:
	// inspired by: https://blog.openreplay.com/resizable-split-panes-from-scratch/
	let resizeDualPanesActive: boolean = $state(false);
	let dualPaneLeftWidth: number = $state(0);
	let dualPaneRightWidth: number = $state(0);
	let dualPaneContainer: HTMLDivElement | null = $state(null);

	// filled in second script tag underneath - after creation of snippets
	const leftPaneData = {
		id: 'leftPane',
		content: leftPane,
		initialRelativeWidth: 1 / 2,
		minWidth: 50,
		maxWidth: 500
	};
	const leftCenterPaneData = { id: 'leftCenterPane', content: leftCenterPane, minWidth: 250 };
	const rightCenterPaneData = {
		id: 'rightCenterPane',
		content: rightCenterPane,
		minWidth: 250,
		maxWidth: 1000
	};
	const rightPaneData = { id: 'rightPane', content: rightPane, minWidth: 250, maxWidth: 400 };

	let panes: PaneData[] = $state([
		leftPaneData,
		leftCenterPaneData,
		rightCenterPaneData,
		rightPaneData
	]);
	// let panesIds: string[] = $derived(panes.map((pane) => pane.id));

	let dataPanes: string[] = $state([
		'Hello Pane 1!',
		'Hello Pane 2!',
		'Hello Pane 3!',
		'Hello Pane 4!'
	]);

	const closePane = (paneId: string) => {
		panes = panes.filter((pane) => pane.id !== paneId);
		// TBD: consider to replace filter with findIndex and splice, if issues with reactivity occur
		// const index = panes.findIndex((pane) => pane.id === paneId);
		// if (index > -1) {
		// 	panes.splice(index, 1);
		// }
	};

	let resizeLeftTriplePanesActive: boolean = $state(false);
	let resizeRightTriplePanesActive: boolean = $state(false);
	let triplePaneContainer: HTMLDivElement | null = $state(null);
	let triplePaneLeftContainer: HTMLDivElement | null = $state(null);
	let triplePaneCenterContainer: HTMLDivElement | null = $state(null);
	let triplePaneRightContainer: HTMLDivElement | null = $state(null);
	let triplePaneLeftWidth: number = $state(0);
	let triplePaneCenterWidth: number = $state(0);
	let triplePaneRightWidth: number = $state(0);

	// constants for layout
	const resizerWidth = 12; // px (Tailwind w-3 ~ 0.75rem)
	const minPane = 80; // px

	// Reactive init when container is ready and widths are zero
	$effect(() => {
		// console.log('=== pane resizing - dualPanes ===');
		// console.log($state.snapshot(dualPanes));
		if (triplePaneLeftContainer) {
			triplePaneLeftWidth = triplePaneLeftContainer.clientWidth + resizerWidth;
		}
		if (triplePaneCenterContainer) {
			triplePaneCenterWidth = triplePaneCenterContainer.clientWidth + resizerWidth;
		}
		if (triplePaneRightContainer) {
			triplePaneRightWidth = triplePaneRightContainer.clientWidth + resizerWidth;
		}
	});

	const startResizingDualPanes = (event: PointerEvent) => {
		// Prevent text selection and mark dragging active
		event.preventDefault();
		(event.currentTarget as HTMLElement)?.setPointerCapture?.(event.pointerId);
		resizeDualPanesActive = true;
	};

	const startResizingLeftTriplePanes = (event: PointerEvent) => {
		// Prevent text selection and mark dragging active
		event.preventDefault();
		(event.currentTarget as HTMLElement)?.setPointerCapture?.(event.pointerId);
		resizeLeftTriplePanesActive = true;
	};

	const startResizingRightTriplePanes = (event: PointerEvent) => {
		// Prevent text selection and mark dragging active
		event.preventDefault();
		(event.currentTarget as HTMLElement)?.setPointerCapture?.(event.pointerId);
		resizeRightTriplePanesActive = true;
	};

	const resizePanes = (event: PointerEvent) => {
		if (resizeDualPanesActive && dualPaneContainer) {
			const rect = dualPaneContainer.getBoundingClientRect();
			// Compute left pane width from absolute mouse position
			const left = event.clientX - rect.left;
			// Setting upper boundary for left pane:
			// ensure right pane >= ( minPane + space for resizer )
			// equals lower boundary for right pane:
			const leftMax = Math.min(left, rect.width - minPane - resizerWidth);
			// sets a lower boundary for the left pane
			// equals upper boundary for right pane:
			dualPaneLeftWidth = Math.max(minPane, leftMax);
			dualPaneRightWidth = rect.width - dualPaneLeftWidth - resizerWidth;
		}
		if (triplePaneContainer) {
			const rect = triplePaneContainer.getBoundingClientRect();
			const totalInner = rect.width - 2 * resizerWidth; // space available for the three panes only

			if (resizeLeftTriplePanesActive) {
				// Dragging the left resizer: adjust Left and Center, keep Right constant
				const x = event.clientX - rect.left; // position from left edge
				const maxLeft = totalInner - triplePaneRightWidth - minPane; // ensure center >= min
				triplePaneLeftWidth = Math.max(minPane, Math.min(x, Math.max(minPane, maxLeft)));
				triplePaneCenterWidth = totalInner - triplePaneLeftWidth - triplePaneRightWidth;
			} else if (resizeRightTriplePanesActive) {
				// Dragging the right resizer: adjust Center and Right, keep Left constant
				const x = event.clientX - rect.left; // position from left edge
				const rightCandidate = rect.width - x - resizerWidth; // width from resizer to right edge
				const maxRight = totalInner - triplePaneLeftWidth - minPane; // ensure center >= min
				triplePaneRightWidth = Math.max(
					minPane,
					Math.min(rightCandidate, Math.max(minPane, maxRight))
				);
				triplePaneCenterWidth = totalInner - triplePaneLeftWidth - triplePaneRightWidth;
			}
		}
	};

	const stopResizingPanes = (_event: PointerEvent) => {
		if (resizeDualPanesActive) {
			resizeDualPanesActive = false;
		} else if (resizeLeftTriplePanesActive) {
			resizeLeftTriplePanesActive = false;
		} else if (resizeRightTriplePanesActive) {
			resizeRightTriplePanesActive = false;
		}
	};
</script>

{#snippet paneTile(color: string, content: string)}
	<div
		class="bg-{color}-container text-{color}-container-content display h-25 w-25 content-center rounded-xl text-center"
	>
		{content}
	</div>
{/snippet}

<!-- <svelte:window use:mapDropdown /> -->
<svelte:window
	onpointermove={resizeDualPanesActive ||
	resizeLeftTriplePanesActive ||
	resizeRightTriplePanesActive
		? resizePanes
		: undefined}
	onpointerup={resizeDualPanesActive || resizeLeftTriplePanesActive || resizeRightTriplePanesActive
		? stopResizingPanes
		: undefined}
/>

{#snippet alphabet(color: string)}
	<!-- <div class="@container/{container}">
				<div
		class="bg-{color}-container/50 text-{color}-container-content rounded-lg @8xl/{container}:grid-cols-9 @10xl/{container}:grid-cols-10 grid h-full grid-cols-1 gap-4 overflow-y-scroll rounded-lg p-4 @xs/{container}:grid-cols-2 @sm/{container}:grid-cols-3 @md/{container}:grid-cols-4 @xl/{container}:grid-cols-5 @2xl/{container}:grid-cols-6 @4xl/{container}:grid-cols-7 @6xl/{container}:grid-cols-8"
		> -->
	<div
		class="bg-{color}-container/50 text-{color}-container-content flex grow flex-wrap justify-end gap-4 rounded-lg p-4"
	>
		{@render paneTile(color, 'A')}
		{@render paneTile(color, 'B')}
		{@render paneTile(color, 'C')}
		{@render paneTile(color, 'D')}
		{@render paneTile(color, 'E')}
		{@render paneTile(color, 'F')}
		{@render paneTile(color, 'G')}
		{@render paneTile(color, 'H')}
		{@render paneTile(color, 'I')}
		{@render paneTile(color, 'J')}
		{@render paneTile(color, 'K')}
		{@render paneTile(color, 'L')}
		{@render paneTile(color, 'M')}
		{@render paneTile(color, 'N')}
		{@render paneTile(color, 'O')}
		{@render paneTile(color, 'P')}
		{@render paneTile(color, 'Q')}
		{@render paneTile(color, 'R')}
		{@render paneTile(color, 'S')}
		{@render paneTile(color, 'T')}
		{@render paneTile(color, 'U')}
		{@render paneTile(color, 'V')}
		{@render paneTile(color, 'W')}
		{@render paneTile(color, 'X')}
		{@render paneTile(color, 'Y')}
		{@render paneTile(color, 'Z')}
	</div>
{/snippet}

{#snippet leftPane()}
	<div class="flex flex-col gap-2 p-4">
		{dataPanes[0]}
		{#if panes.some((pane) => pane.id === 'leftPane')}
			<button class="btn btn-success" onclick={() => closePane('leftPane')}>Close pane 1</button>
		{:else}
			<button class="btn btn-primary" onclick={() => panes.push(leftPaneData)}>
				Open pane 1
			</button>
		{/if}
		{#if panes.some((pane) => pane.id === 'leftCenterPane')}
			<button class="btn btn-warning" onclick={() => closePane('leftCenterPane')}
				>Close pane 2</button
			>
		{/if}
		{#if panes.some((pane) => pane.id === 'rightCenterPane')}
			<button class="btn btn-error" onclick={() => closePane('rightCenterPane')}
				>Close pane 3</button
			>
		{/if}
		{#if panes.some((pane) => pane.id === 'rightPane')}
			<button class="btn btn-info" onclick={() => closePane('rightPane')}>Close pane 4</button>
		{/if}
	</div>
	{@render alphabet('success')}
{/snippet}
{#snippet leftCenterPane()}
	<div class="p-4">
		{dataPanes[1]}
	</div>
	{@render alphabet('warning')}
{/snippet}
{#snippet rightCenterPane()}
	<!-- {@render alphabet('error', 'rightCenterPane')} -->
	<div class="p-4">
		{dataPanes[2]}
	</div>
	<div class="@container/rightCenterPane rounded-lg">
		<div
			class="bg-error-container/50 text-error-container-content @8xl/rightCenterPane:grid-cols-9 @10xl/rightCenterPane:grid-cols-10 grid h-full grid-cols-1 gap-4 overflow-y-scroll rounded-lg p-4 @xs/rightCenterPane:grid-cols-2 @sm/rightCenterPane:grid-cols-3 @md/rightCenterPane:grid-cols-4 @xl/rightCenterPane:grid-cols-5 @2xl/rightCenterPane:grid-cols-6 @4xl/rightCenterPane:grid-cols-7 @6xl/rightCenterPane:grid-cols-8"
		>
			{@render paneTile('error', 'A')}
			{@render paneTile('error', 'B')}
			{@render paneTile('error', 'C')}
			{@render paneTile('error', 'D')}
			{@render paneTile('error', 'E')}
			{@render paneTile('error', 'F')}
			{@render paneTile('error', 'G')}
			{@render paneTile('error', 'H')}
			{@render paneTile('error', 'I')}
			{@render paneTile('error', 'J')}
			{@render paneTile('error', 'K')}
			{@render paneTile('error', 'L')}
			{@render paneTile('error', 'M')}
			{@render paneTile('error', 'N')}
			{@render paneTile('error', 'O')}
			{@render paneTile('error', 'P')}
			{@render paneTile('error', 'Q')}
			{@render paneTile('error', 'R')}
			{@render paneTile('error', 'S')}
			{@render paneTile('error', 'T')}
			{@render paneTile('error', 'U')}
			{@render paneTile('error', 'V')}
			{@render paneTile('error', 'W')}
			{@render paneTile('error', 'X')}
			{@render paneTile('error', 'Y')}
			{@render paneTile('error', 'Z')}
		</div>
	</div>
{/snippet}
{#snippet rightPane()}
	<div class="p-4">
		{dataPanes[3]}
		<div class="input-filled input-success shadow-base-shadow w-100 rounded-md shadow-inner">
			<input
				type="text"
				placeholder="Data for left Pane"
				class="input input-xl"
				id="leftPaneInput"
				bind:value={dataPanes[0]}
			/>
			<label class="input-filled-label" for="leftPaneInput">Data for Left Pane:</label>
		</div>
	</div>
	{@render alphabet('info')}
{/snippet}

<div class="flex flex-col justify-around sm:flex-row">
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base" for="prodSwitcher">Production: off </label>
		<input type="checkbox" class="switch switch-accent" bind:checked={prod} id="prodSwitcher" />
		<label class="label label-text text-base" for="prodSwitcher"> on</label>
	</div>
	<div class="mb-2 flex items-center gap-1">
		<label class="label label-text text-base" for="developSwitcher">🚧 Development 🚧: off </label>
		<input
			type="checkbox"
			class="switch switch-accent"
			bind:checked={develop}
			id="developSwitcher"
		/>
		<label class="label label-text text-base" for="developSwitcher"> on</label>
	</div>
</div>

<!-- <JsonData data={page.url} />
<JsonData data={page.url.search} />
<JsonData data={page.url.searchParams.get("develop")} /> -->

{#snippet underConstruction()}
	<p class="text-center">
		Not in production yet - check out the <a class="link" href="?develop=true"
			>🚧 development version 🚧</a
		>.
	</p>
{/snippet}

<div
	class="w-full {prod && develop
		? 'md:grid md:grid-cols-2 md:gap-4'
		: 'xl:grid xl:grid-cols-2 xl:gap-4'}"
>
	<div class={prod ? 'block' : 'hidden'}>
		<Title id="card-with-chat">Card with chat</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="card-with-chat-dev">🚧 Card with chat 🚧</Title>
		<div class="mb-5 grid justify-items-center">
			{#snippet headerChat()}
				<h5 class="title md:title-large card-title">Chat card</h5>
			{/snippet}
			<Card id="chatCard" extraClasses="md:w-4/5" header={headerChat} footer={footerChat}>
				<div
					class="bg-base-150 shadow-outline max-h-96 min-h-44 overflow-y-auto rounded-lg p-2 shadow-inner"
				>
					<div class="chat chat-receiver">
						<div class="avatar chat-avatar">
							<div class="size-10 rounded-full">
								<span class="icon-[tabler--man] text-primary m-1 size-8"></span>
							</div>
						</div>
						<div class="chat-header text-base-content">
							User 1
							<time class="text-base-content/50">12:45</time>
						</div>
						<div class="chat-bubble-primary chat-bubble">Message from user 1.</div>
						<div class="chat-footer text-base-content/50">
							<div>Read</div>
						</div>
					</div>
					<div class="chat chat-receiver">
						<div class="avatar chat-avatar">
							<div class="size-10 rounded-full">
								<span class="icon-[tabler--user] text-primary m-1 size-8"></span>
							</div>
						</div>
						<div class="chat-header text-base-content">
							User 2
							<time class="text-base-content/50">12:57</time>
						</div>
						<div class="chat-bubble-primary chat-bubble">User 2 also had something to say.</div>
						<div class="chat-footer text-base-content/50">
							<div>Read</div>
						</div>
					</div>
					<div class="chat chat-sender">
						<div class="chat-header text-base-content">
							You
							<time class="text-base-content/50">13:27</time>
						</div>
						<div class="chat-bubble-secondary chat-bubble">And I have replied to that.</div>
						<div class="chat-footer text-base-content/50">
							<div>Delivered</div>
						</div>
					</div>
				</div>
			</Card>
			{#snippet footerChat()}
				<div class="flex flex-row items-center gap-2">
					<div class="input-filled grow">
						<input type="text" placeholder="Send a message here" class="input" id="chatMessage" />
						<label
							class="input-filled-label"
							style="color: var(--color-secondary);"
							for="chatMessage">♡ What's on your heart?</label
						>
					</div>
					<button
						class="btn-secondary-container btn btn-circle btn-gradient"
						aria-label="Send Icon Button"
					>
						<span class="icon-[tabler--send-2]"></span>
					</button>
				</div>
			{/snippet}
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="card-with-text-and-title-navigation">Card with text and title navigation</Title>
		<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
			{#each cardsNavigation as cardNavigation, i (i)}
				<NavigationCard title={cardNavigation.title} href={cardNavigation.link}
					>{cardNavigation.description}</NavigationCard
				>
			{/each}
		</div>
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="card-with-text-and-title-navigation-dev"
			>🚧 Card with text and title navigation 🚧</Title
		>
		<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
			<div
				class="card border-outline-variant bg-base-250 shadow-outline-variant rounded-xl border-[1px] shadow-lg"
			>
				<div class="card-header">
					<a href="#top" class="link link-base-content link-animated">
						<h5 class="title-small md:title lg:title-large base-content card-title">
							Here's a title
						</h5>
					</a>
				</div>
				<div class="card-body">
					<p class="body-small md:body text-primary-container-content">
						Some test text, here. Can go over several lines. And if it does, the cards in the same
						line will adjust to the longest card. This is a good way to keep the layout clean and
						consistent.
					</p>
				</div>
			</div>
			<div
				class="card border-outline-variant bg-base-250 shadow-outline-variant rounded-xl border-[1px] shadow-lg"
			>
				<div class="card-header">
					<a href="#top" class="link link-base-content link-animated">
						<h5 class="title-small md:title lg:title-large base-content card-title">
							One more title
						</h5>
					</a>
				</div>
				<div class="card-body">
					<p class="body-small md:body text-primary-container-content">
						Some shorter text here - but adjusts to the height of the neighbor card
					</p>
				</div>
			</div>
			<div
				class="card border-outline-variant bg-base-250 shadow-outline-variant rounded-xl border-[1px] shadow-lg"
			>
				<div class="card-header">
					<a href="#top" class="link link-base-content link-animated">
						<h5 class="title-small md:title lg:title-large base-content card-title">
							A third title
						</h5>
					</a>
				</div>
				<div class="card-body">
					<p class="body-small md:body text-primary-container-content">
						This one is meant to fill the row. Note how the cards are responsive on smaller screens.
					</p>
				</div>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="card-with-dropdown-menu">Card with dropdown menu</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="card-with-dropdown-menu-dev">🚧 Card with dropdown menu 🚧</Title>
		<div class="mb-5 grid justify-items-center">
			{#snippet headerEdit()}
				<div class="flex justify-between">
					<div>
						<h5 class="title md:title-large card-title">Card with editable text</h5>
					</div>
					<div class="flex flex-row items-start gap-4">
						<div class="dropdown relative inline-flex rtl:[--placement:bottom-end]">
							<span
								id="dropdown-menu-icon"
								class="dropdown-toggle icon-[tabler--dots-vertical] size-6"
								role="button"
								aria-haspopup="menu"
								aria-expanded="false"
								aria-label="Dropdown"
							></span>
							<ul
								class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden shadow-xs"
								role="menu"
								aria-orientation="vertical"
								aria-labelledby="dropdown-menu-icon"
							>
								<li class=" items-center">
									<button class="btn dropdown-item btn-text justify-start"
										><span class="icon-[material-symbols--edit-outline-rounded]"></span> Edit</button
									>
								</li>
								<li class="items-center">
									<button class="btn dropdown-item btn-text justify-start"
										><span class="icon-[tabler--share-2]"></span>Share</button
									>
								</li>
								<li class="dropdown-footer gap-2">
									<button class="btn dropdown-item btn-error btn-text justify-start"
										><span class="icon-[tabler--trash]"></span>Delete</button
									>
								</li>
							</ul>
						</div>
					</div>
				</div>
			{/snippet}
			<Card id="cardEdit" extraClasses="md:w-4/5" header={headerEdit}>
				<div
					class="bg-base-150 shadow-outline max-h-96 min-h-44 overflow-y-auto rounded-lg p-2 shadow-inner"
				>
					Some text
				</div>
			</Card>
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="card-with-action-buttons">Card with action buttons</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="card-with-action-buttons-dev">🚧 Card with action buttons 🚧</Title>
		<div class="mb-5 grid justify-items-center">
			{#snippet footerAction()}
				<div class="join flex flex-row items-center justify-center">
					<button
						class="btn btn-secondary-container text-secondary-container-content join-item grow"
						aria-label="Edit Button"
						onclick={() => (edit ? (edit = false) : (edit = true))}
					>
						<span class="icon-[material-symbols--edit-outline-rounded]"></span>Edit
					</button>
					<div
						class="dropdown join-item relative inline-flex grow [--auto-close:inside] [--placement:top]"
						bind:this={actionButtonShareMenu}
						{@attach initDropdown}
					>
						<button
							id="action-share"
							class="dropdown-toggle btn btn-secondary-container text-secondary-container-content w-full rounded-none"
							aria-haspopup="menu"
							aria-expanded="false"
							aria-label="Share with"
						>
							<span class="icon-[tabler--share-2]"></span>Share
							<span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-4"></span>
						</button>
						<ul
							class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden min-w-[15rem] shadow-xs"
							role="menu"
							aria-orientation="vertical"
							aria-labelledby="action-share"
						>
							<!-- {#each shareOptions as shareOption, i (i)}
								<ShareItem
									resourceId="actionButtonShareResourceId"
									{shareOption}
									{handleRightsChangeResponse}
								/>
							{/each} -->
							<form
								method="POST"
								name="actionButtonShareForm"
								use:enhance={async () => {
									window.HSDropdown.close(actionButtonShareMenu);
									return async ({ result, update }) => {
										handleRightsChangeResponse(result, update);
									};
								}}
							>
								{#each shareOptions as shareOption, i (i)}
									<ShareItem resourceId="actionButtonShareResourceId" {shareOption} />
								{/each}
							</form>
							<li class="dropdown-footer gap-2">
								<button
									class="btn dropdown-item btn-text text-secondary content-center justify-start"
									>... more options</button
								>
							</li>
						</ul>
					</div>
					<button
						class="btn btn-error-container bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content join-item grow border-0"
						aria-label="Delete Button"
						name="id"
						formaction="?/delete"
					>
						<span class="icon-[tabler--trash]"></span>Delete
					</button>
				</div>
			{/snippet}
			<Card id="cardEdit" footer={footerAction}>
				<p class="body-small md:body text-primary-container-content">
					The footer of this card contains action buttons.
				</p>
			</Card>
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="buttons">Buttons</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="buttons-dev">🚧 Buttons 🚧</Title>
		<div class="flex flex-row gap-4">
			<button class="btn btn-accent-container btn-gradient shadow-outline rounded-full shadow-sm"
				><span class="icon-[tabler--chevron-right]"></span>Big button</button
			>
			<button
				class="btn btn-success-container btn-gradient shadow-outline btn-circle shadow-sm"
				aria-label="Open in Microsoft Teams"
			>
				<span class="icon-[tabler--send-2]"></span>
			</button>
			<a href="./" aria-label="Top">
				<button
					class="btn btn-info-container btn-gradient shadow-outline btn-circle shadow-sm"
					aria-label="Top"
				>
					<span class="icon-[tabler--link]"></span>
				</button>
			</a>
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="dropdown-menus">Dropdown menus</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="dropdown-menus-dev">🚧 Dropdown menus 🚧</Title>
		<div class="mb-20 flex flex-wrap gap-4">
			<div
				class="dropdown relative inline-flex rtl:[--placement:bottom-end]"
				bind:this={dropdownMenu}
				{@attach initDropdown}
			>
				<div
					id="dropdown-menu-icon"
					role="button"
					class="dropdown-toggle"
					aria-haspopup="menu"
					aria-expanded="false"
					aria-label="Dropdown"
				>
					<span class="icon-[tabler--dots-vertical] text-secondary size-6"></span>
				</div>
				<ul
					class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden shadow-xs"
					role="menu"
					aria-orientation="vertical"
					aria-labelledby="dropdown-menu-icon"
				>
					<li class="items-center">
						<button
							class="btn dropdown-item btn-text text-secondary content-center justify-start"
							aria-label="Edit Button"
							onclick={() => (edit ? (edit = false) : (edit = true))}
						>
							<span class="icon-[material-symbols--edit-outline-rounded]"></span> Edit
						</button>
					</li>
					<li
						class="dropdown relative items-center [--auto-close:inside] [--offset:15] [--placement:right-start] max-sm:[--placement:bottom-start]"
						bind:this={dropdownShareDropdown}
						{@attach initDropdown}
					>
						<button
							id="share"
							class="dropdown-toggle btn dropdown-item btn-text text-secondary content-center justify-start"
							aria-haspopup="menu"
							aria-expanded="false"
							aria-label="Share with"
						>
							<span class="icon-[tabler--share-2]"></span>
							Share
							<span class="icon-[tabler--chevron-right] size-4 rtl:rotate-180"></span>
						</button>
						<ul
							class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden min-w-[15rem] shadow-xs"
							role="menu"
							aria-orientation="vertical"
							aria-labelledby="share"
						>
							<!-- {#each shareOptions as shareOption, i (i)}
								<ShareItem
									resourceId="dropdownShareDropdownResourceId"
									{shareOption}
									{handleRightsChangeResponse}
								/>
							{/each} -->
							<form
								method="POST"
								name="dropDownShareDropdownForm"
								use:enhance={async () => {
									window.HSDropdown.close(dropdownMenu);
									window.HSDropdown.close(dropdownShareDropdown);
									return async ({ result, update }) => {
										handleRightsChangeResponse(result, update);
									};
								}}
							>
								{#each shareOptions as shareOption, i (i)}
									<ShareItem resourceId="dropdownShareDropdownResourceId" {shareOption} />
								{/each}
							</form>
							<li class="dropdown-footer gap-2">
								<button
									class="btn dropdown-item btn-text text-secondary content-center justify-start"
									>... more options</button
								>
							</li>
						</ul>
					</li>
					<li class="dropdown-footer gap-2">
						<button
							class="btn dropdown-item btn-error btn-text text-secondary content-center justify-start"
							aria-label="Delete Button"
							name="id"
							formaction="?/delete"><span class="icon-[tabler--trash]"></span>Delete</button
						>
					</li>
				</ul>
			</div>
			<div>
				<div
					class="dropdown relative inline-flex [--auto-close:inside]"
					bind:this={dropdownShare}
					{@attach initDropdown}
				>
					<button
						id="dropdown-share"
						type="button"
						class="dropdown-toggle btn btn-secondary-container text-secondary-container-content w-full"
						aria-haspopup="menu"
						aria-expanded="false"
						aria-label="Share with"
					>
						<span class="icon-[tabler--share-2]"></span>Share
						<span class="icon-[tabler--chevron-down] dropdown-open:rotate-180 size-4"></span>
					</button>
					<ul
						class="dropdown-menu dropdown-open:opacity-100 bg-base-300 hidden min-w-60"
						role="menu"
						aria-orientation="vertical"
						aria-labelledby="dropdown-share"
					>
						<!-- <ShareItem
							resourceId="dropdownShareResourceId"
							shareOption={shareOptions[0]}
							{handleRightsChangeResponse}
						/> -->
						<form
							method="POST"
							name="dropdownShareForm"
							use:enhance={async () => {
								window.HSDropdown.close(dropdownShare);
								return async ({ result, update }) => {
									handleRightsChangeResponse(result, update);
								};
							}}
						>
							<ShareItem resourceId="dropdownShareResourceId" shareOption={shareOptions[0]} />
						</form>
					</ul>
				</div>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="selections">Selections</Title>
		{@render underConstruction()}
	</div>

	{#snippet shareSelectOptionIcon(right: Action | undefined)}
		<span class={AccessHandler.rightsIcon(right)}></span>
	{/snippet}

	{#snippet shareSelectOption(right: Action | undefined)}
		{#if browser === 'Firefox' || browser === 'Safari'}
			<option
				class="dropdown-item dropdown-close bg-base-300 text-{AccessHandler.rightsIconColor(
					right
				)} custom-option-own border-none"
				value={right}
			>
				<!-- TBD: add emojis as alternative for older browsers! -->
				{AccessHandler.rightsIconEmoji(right)}&nbsp;{right || 'none'}
			</option>
		{:else}
			<option
				class="dropdown-item dropdown-close bg-base-300 text-{AccessHandler.rightsIconColor(
					right
				)} custom-option-own border-none"
				value={right}
			>
				{@render shareSelectOptionIcon(right)}
				{right || 'none'}
			</option>
			<!-- <span class={AccessHandler.rightsIcon(right)}></span> -->
		{/if}
	{/snippet}
	<div class={develop ? 'block' : 'hidden'}>
		<Title id="selections-dev">🚧 Selections 🚧</Title>
		<div class="bg-base-300 mb-20 flex w-fit flex-wrap gap-4 rounded rounded-xl p-4">
			<div class="relative flex items-center [--placement:top]">
				<!-- <div class="relative flex flex-row"> -->
				<form
					class="w-fit"
					method="POST"
					name="selection-right-form"
					action={`?/share&identity-id=${shareOptions[1].identity_id}&action=${desiredActions(selectedAction).action}&new-action=${desiredActions(selectedAction).new_action}`}
					use:enhance={async ({ formData }) => {
						formData.append('id', 'selection-resource-id');
						return async ({ result, update }) => {
							handleRightsChangeResponse(result, update);
						};
					}}
				>
					<select
						class="select custom-select bg-base-300 -mx-4 w-full {AccessHandler.rightsIcon(
							shareOptions[1].action
						)}  size-6"
						id="rights-{shareOptions[1].identity_id}-selection"
						required
						aria-label="Select rights"
						name="right"
						onclick={() => (selectionFocused = !selectionFocused)}
						onchange={(event) => {
							if (share) {
								// 	share({
								// 	resource_id: resourceId,
								// 	identity_id: shareOption.identity_id,
								// 	action: desiredActions(selectedAction).action,
								// 	new_action: desiredActions(selectedAction).new_action
								// });
								// if (closeShareMenu) {
								// 	closeShareMenu();
								// }
							} else {
								const form = (event.target as HTMLSelectElement).form;
								form?.requestSubmit();
							}
						}}
						bind:value={selectedAction}
					>
						{@render shareSelectOption(Action.OWN)}
						{@render shareSelectOption(Action.WRITE)}
						{@render shareSelectOption(Action.READ)}
						{@render shareSelectOption(undefined)}
					</select>
				</form>
				<span
					class="icon-[tabler--chevron-down] bg-secondary pointer-events-none absolute top-1/2 right-2 size-6 -translate-y-1/2 transition-transform duration-400"
					class:rotate-180={selectionFocused}
				>
				</span>
			</div>
			<!-- <select
				class="select select-floating max-w-sm"
				onclick={() => {
					if (share) {
						share({
							resource_id: resourceId,
							identity_id: shareOption.identity_id,
							action: desiredActions(selectedAction).action,
							new_action: desiredActions(selectedAction).new_action
						});
						// if (closeShareMenu) {
						// 	closeShareMenu();
						// }
					} else {
						goto(
							`?/share&identity-id=${shareOption.identity_id}&action=${desiredActions(selectedAction).action}&new-action=${desiredActions(selectedAction).new_action}`
						);
					}
				}}
				bind:value={selectedAction}
			>
			</select>
		</div> -->
		</div>
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="status-sliders">Status sliders with Hue-Chroma-Tone</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="status-sliders-dev">🚧 Status sliders with Hue-Chroma-Tone 🚧</Title>
		<div class="grid grid-cols-3 gap-4">
			<div class="w-full">
				<label class="label label-text" for="leftStatus"
					>Left Color: <span class="label">
						<code class="label-text-alt">{status[0]}</code>
					</span></label
				>
				<input
					type="range"
					min="0"
					max="100"
					step="1"
					class="range w-full"
					aria-label="left Status"
					id="leftStatus"
					bind:value={status[0]}
				/>
			</div>
			<div class="w-full">
				<label class="label label-text" for="leftStatus"
					>Center Color: <span class="label">
						<code class="label-text-alt">{status[1]}</code>
					</span></label
				>
				<input
					type="range"
					min="0"
					max="100"
					step="1"
					class="range w-full"
					aria-label="center Status"
					id="centerStatus"
					bind:value={status[1]}
				/>
			</div>
			<div class="w-full">
				<label class="label label-text" for="leftStatus"
					>Right Color: <span class="label">
						<code class="label-text-alt">{status[2]}</code>
					</span></label
				>
				<input
					type="range"
					min="0"
					max="100"
					step="1"
					class="range w-full"
					aria-label="right Status"
					id="rightStatus"
					bind:value={status[2]}
				/>
			</div>
		</div>
		<div class="grid grid-cols-3 overflow-hidden rounded-2xl">
			<div
				class="flex h-20 w-full items-center justify-center text-3xl font-bold"
				style="background: linear-gradient(to right, {statusColors[0].background}, {statusColors[0]
					.background}, {statusColors[1].background}); color: {statusColors[0].text};"
			>
				Left
			</div>
			<div
				class="flex h-20 w-full items-center justify-center text-3xl font-bold"
				style="background: linear-gradient(to right, {statusColors[1].background}, {statusColors[1]
					.background}, {statusColors[1].background}); color: {statusColors[1].text};"
			>
				Center
			</div>
			<div
				class="flex h-20 w-full items-center justify-center text-3xl font-bold"
				style="background: linear-gradient(to right, {statusColors[1].background}, {statusColors[2]
					.background}, {statusColors[2].background}); color: {statusColors[2].text};"
			>
				Right
			</div>
			<!-- <div
					class="flex h-20 w-full items-center justify-center text-2xl"
					style="background: linear-gradient(to right, {statusColors[1]}, {statusColors[2]});"
				></div> -->
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="tooltips">Tooltips</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="tooltips-dev">🚧 Tooltips 🚧</Title>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div class="tooltip" {@attach initTooltip}>
				<button type="button" class="tooltip-toggle btn btn-square" aria-label="Tooltip">
					<span class="icon-[tabler--chevron-up]"></span>
				</button>
				<span
					class="tooltip-content tooltip-shown:visible tooltip-shown:opacity-100"
					role="tooltip"
				>
					<span class="tooltip-body">Tooltip on top</span>
				</span>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="theme-picker">Theme Picker</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="theme-picker-dev">🚧 Theme Picker 🚧</Title>
		<p class="title-large text-primary">Building blocks</p>
		<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
			<div class="w-48">
				<label class="label label-text" for="colorPicker"
					>Source color
					<span class="label">
						<code class="label-text-alt">{sourceColor}</code>
					</span>
				</label>
				<input
					class="w-full"
					type="color"
					id="colorPicker"
					name="color-picker"
					onblur={() => console.log('=== color selector blurred ===')}
					bind:value={sourceColor}
				/>
			</div>
			<div class="relative w-48">
				<label class="label label-text" for="themeVariant">Variant</label>
				<select
					class="select select-floating max-w-sm"
					aria-label="Select variant"
					id="themeVariant"
					onblur={() => console.log('=== variant selector blurred ===')}
					bind:value={variant}
				>
					<option value={Variant.TONAL_SPOT}>Tonal Spot</option>
					<!-- <option value={Variant.MONOCHROME}>Monochrome</option> -->
					<option value={Variant.NEUTRAL}>Neutral</option>
					<option value={Variant.VIBRANT}>Vibrant</option>
					<!-- <option value={Variant.EXPRESSIVE}>Expressive</option> -->
					<option value={Variant.FIDELITY}>Fidelity</option>
					<option value={Variant.CONTENT}>Content</option>
					<option value={Variant.RAINBOW}>Rainbow</option>
					<!-- <option value={Variant.FRUIT_SALAD}>Fruit Salad</option> -->
				</select>
			</div>
			<div class="w-48">
				<label class="label label-text" for="contrast"
					>Contrast: <span class="label">
						<code class="label-text-alt">{contrast}</code>
					</span></label
				>

				<input
					type="range"
					min={contrastMin}
					max={contrastMax}
					step={contrastStep}
					class="range w-full"
					aria-label="contrast"
					id="contrast"
					onblur={() => console.log('=== contrast slider blurred ===')}
					bind:value={contrast}
				/>
				<div class="flex w-full justify-between px-2 text-xs">
					{#each allContrasts as _ (_)}
						<span>|</span>
					{/each}
				</div>
			</div>
		</div>
		<p class="title-large text-primary">as SvelteComponent</p>
		<ul
			class="bg-base-200 text-neutral shadow-outline w-fit rounded-xl p-4 shadow-md"
			role="menu"
			aria-orientation="vertical"
			aria-labelledby="dropdown-menu-icon-user"
		>
			<ThemePicker
				{updateProfileAccount}
				{saveProfileAccount}
				bind:themeForm
				bind:mode
				{themeConfiguration}
			/>
		</ul>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="caroussels">Caroussels</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="caroussels-dev">🚧 Caroussels 🚧</Title>
		<!-- TBD: pass those data-carousel arguments:
		 " '{' "loadingClasses": "opacity-0" '}'" -->
		<div id="vertical-thumbnails" data-carousel class="relative w-full">
			<div class="carousel flex space-x-2 rounded-none" {@attach initCarousel}>
				<div class="flex-none">
					<div
						class="carousel-pagination flex h-full w-[200px] flex-col justify-between gap-y-2 overflow-hidden max-sm:w-8"
					>
						<img
							src="/matterhorn-20230628.jpg"
							class="carousel-pagination-item carousel-active:opacity-100 grow rounded-lg object-cover opacity-30"
							alt="Swiss mountain Matterhorn in sunset"
						/>
						<img
							src="/mountain-salamander-20240702.jpg"
							class="carousel-pagination-item carousel-active:opacity-100 grow rounded-lg object-cover opacity-30"
							alt="Mountain salamander on a rock"
						/>
						<img
							src="/starnberger-see-unset-20230807.jpg"
							class="carousel-pagination-item carousel-active:opacity-100 grow rounded-lg object-cover opacity-30"
							alt="Bavarian lake Starnberger See in sunset"
						/>
					</div>
				</div>
				<div class="relative grow overflow-hidden rounded-2xl">
					<div class="carousel-body h-80 opacity-0">
						<!-- Slide 1 -->
						<div class="carousel-slide">
							<div class="flex size-full justify-center">
								<img
									src="/matterhorn-20230628.jpg"
									class="size-full object-cover"
									alt="Swiss mountain Matterhorn in sunset"
								/>
							</div>
						</div>
						<!-- Slide 2 -->
						<div class="carousel-slide">
							<div class="flex size-full justify-center">
								<img
									src="/mountain-salamander-20240702.jpg"
									class="size-full object-cover"
									alt="Mountain Salamander on a rock"
								/>
							</div>
						</div>
						<!-- Slide 3 -->
						<div class="carousel-slide">
							<div class="flex size-full justify-center">
								<img
									src="/starnberger-see-unset-20230807.jpg"
									class="size-full object-cover"
									alt="Bavarian lake Starnberger See in sunset"
								/>
							</div>
						</div>
					</div>
					<!-- Previous Slide -->
					<button
						type="button"
						class="carousel-prev carousel-disabled:opacity-50 bg-base-100 shadow-base-300/20 start-5 flex size-9.5 items-center justify-center rounded-full shadow-sm max-sm:start-3"
					>
						<span class="icon-[tabler--chevron-left] size-5 cursor-pointer"></span>
						<span class="sr-only">Previous</span>
					</button>
					<!-- Next Slide -->
					<button
						type="button"
						class="carousel-next carousel-disabled:opacity-50 bg-base-100 shadow-base-300/20 end-5 flex size-9.5 items-center justify-center rounded-full shadow-sm max-sm:end-3"
					>
						<span class="icon-[tabler--chevron-right] size-5"></span>
						<span class="sr-only">Next</span>
					</button>
				</div>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="vertical-tabs">Vertical Tabs</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="vertical-tabs-dev">🚧 Vertical Tabs 🚧</Title>
		<div class="flex">
			<div
				class="tabs tabs-bordered tabs-vertical w-[130px]"
				aria-label="Tabs"
				role="tablist"
				data-tabs-vertical="true"
				aria-orientation="horizontal"
				{@attach initTabs}
			>
				<button
					type="button"
					class="tab active-tab:tab-active active py-11 text-left"
					id="tabs-vertical-item-welcome"
					data-tab="#tabs-vertical-welcome"
					aria-controls="tabs-vertical-welcome"
					role="tab"
					aria-selected="true"
				>
					Welcome
				</button>
				<button
					type="button"
					class="tab active-tab:tab-active py-11 text-left"
					id="tabs-vertical-item-ai"
					data-tab="#tabs-vertical-ai"
					aria-controls="tabs-vertical-ai"
					role="tab"
					aria-selected="false"
				>
					Artificial Intelligence
				</button>
				<button
					type="button"
					class="tab active-tab:tab-active py-11 text-left"
					id="tabs-vertical-item-theme"
					data-tab="#tabs-vertical-theme"
					aria-controls="tabs-vertical-theme"
					role="tab"
					aria-selected="false"
				>
					Theme Configuration
				</button>
			</div>

			<div class="h-[245px] w-[264px]">
				<div
					class="relative flex h-full w-full"
					id="tabs-vertical-welcome"
					role="tabpanel"
					aria-labelledby="tabs-vertical-item-welcome"
				>
					<div
						class="absolute inset-0 m-1 h-full w-full bg-[url(/matterhorn-20230628.jpg)] mask-y-from-95% mask-y-to-100% mask-x-from-95% mask-x-to-100% bg-cover bg-center p-4 opacity-70"
					></div>
					<div
						class="text-base-content/80 relative m-1 h-full w-full content-center rounded-xl p-4"
					>
						Welcome to the
						<div class="align-center flex flex-row justify-center">
							<div class="flex flex-col justify-center">
								<div class="title-small text-primary italic" style="line-height: 1;">Fullstack</div>
								<div
									class="title-small text-secondary font-bold tracking-widest"
									style="line-height: 1"
								>
									Sandbox
								</div>
							</div>
							<div class="Title-large navbar-center text-accent ml-1 flex items-center">23</div>
						</div>
						<div class="text-right">Have fun exploring the content and trying things out!</div>
					</div>
				</div>
				<div
					id="tabs-vertical-ai"
					class="mx-5 hidden h-full"
					role="tabpanel"
					aria-labelledby="tabs-vertical-item-ai"
				>
					<ul
						class="m-1 h-full w-full p-4"
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
					</ul>
				</div>
				<div
					id="tabs-vertical-theme"
					class="mx-5 hidden"
					role="tabpanel"
					aria-labelledby="tabs-vertical-item-theme"
				>
					<ul
						class="m-1 w-fit p-4"
						role="menu"
						aria-orientation="vertical"
						aria-labelledby="dropdown-menu-icon-user"
					>
						<ThemePicker
							{updateProfileAccount}
							{saveProfileAccount}
							bind:themeForm
							bind:mode
							bind:themeConfiguration
						/>
					</ul>
				</div>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<!-- {#snippet paneTile(color: string, content: string)}
		<div
			class="bg-{color}-container text-{color}-container-content display h-25 w-25 content-center rounded-xl text-center"
		>
			{content}
		</div>
	{/snippet} -->
	<div class={prod ? 'block' : 'hidden'}>
		<Title id="horizontal-diffs">Horizontal Diffs</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="horizontal-diffs-dev">🚧 Horizontal Diffs 🚧</Title>
		<div>
			<p class="title text-primary">Two images, horizontal resizing.</p>
			<div class="diff aspect-video rounded-2xl" bind:clientWidth={diffWidth}>
				<div class="diff-item-1" bind:clientWidth={firstDiffWidth}>
					<img
						alt="Bavarian lake Starnberger See in sunset"
						src="/starnberger-see-unset-20230807.jpg"
					/>
				</div>
				<div class="diff-item-2" bind:clientWidth={secondDiffWidth}>
					<img alt="Swiss mountain Matterhorn in sunset" src="/matterhorn-20230628.jpg" />
				</div>
				<div class="diff-resizer" bind:this={resizerDiff}></div>
			</div>
			<p class="caption text-primary-container-content mt-2 text-center text-sm">
				Drag the divider to compare the two images.
			</p>
			<div class="text-primary-container-content mx-20 flex flex-row justify-between text-sm">
				<div>Left Width: {firstDiffWidth}</div>
				<div>Resizer Position: {resizerDiff?.clientWidth}</div>
				<div>Right Width: {diffWidth - secondDiffWidth}</div>
			</div>

			<div class="text-center">
				<button
					type="button"
					class="btn btn-secondary-container btn-sm mt-4"
					onclick={() => {
						if (resizerDiff) {
							resizerDiff.style.width = diffWidth / 2 + 'px';
						}
					}}
				>
					Reset Resizer Position
				</button>
			</div>

			<div class="mt-10">
				<p class="title text-primary">Resizing two flex containers with adoptive content size.</p>
				<div class="diff aspect-video rounded-2xl" bind:clientWidth={diffWidthAdoptiveFlex}>
					<div class="diff-item-1 h-full">
						<div class="flex h-full justify-end">
							<div
								class="bg-secondary flex flex-wrap justify-end gap-4 p-4"
								style={`width: ${firstDiffWidthAdoptiveFlex}px;`}
							>
								{@render paneTile('secondary', '1')}
								{@render paneTile('secondary', '2')}
								{@render paneTile('secondary', '3')}
								{@render paneTile('secondary', '4')}
							</div>
						</div>
					</div>
					<div class="diff-item-2" bind:clientWidth={secondDiffWidthAdoptiveFlex}>
						<div class="bg-primary flex w-full flex-wrap gap-4 p-4">
							{@render paneTile('primary', 'A')}
							{@render paneTile('primary', 'B')}
							{@render paneTile('primary', 'C')}
							{@render paneTile('primary', 'D')}
						</div>
					</div>
					<div class="diff-resizer"></div>
				</div>
			</div>
			<div class="mt-10">
				<p class="title text-primary">Resizing two grids with adoptive content size.</p>
				<div class="diff h-100 rounded-2xl" bind:clientWidth={diffWidthAdoptiveGrid}>
					<div class="diff-item-1">
						<div class="flex justify-end">
							<div class="@container/diff1" style={`width: ${firstDiffWidthAdoptiveGrid}px;`}>
								<div
									class="bg-info grid h-full grid-cols-1 justify-items-end gap-4 overflow-y-auto p-4 @2xs/diff1:grid-cols-2 @md/diff1:grid-cols-3 @lg/diff1:grid-cols-4"
								>
									{@render paneTile('info', '1')}
									{@render paneTile('info', '2')}
									{@render paneTile('info', '3')}
									{@render paneTile('info', '4')}
								</div>
							</div>
						</div>
					</div>
					<div class="diff-item-2 @container/diff2" bind:clientWidth={secondDiffWidthAdoptiveGrid}>
						<div
							class="bg-accent grid w-full grid-cols-1 gap-4 overflow-y-auto p-4 @2xs/diff2:grid-cols-2 @md/diff2:grid-cols-3 @lg/diff2:grid-cols-4"
						>
							{@render paneTile('accent', 'A')}
							{@render paneTile('accent', 'B')}
							{@render paneTile('accent', 'C')}
							{@render paneTile('accent', 'D')}
						</div>
					</div>
					<div class="diff-resizer"></div>
				</div>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="vertical-diffs">Vertical Diffs</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="vertical-diffs-dev">🚧 Vertical Diffs 🚧</Title>
		<div class="mt-10 flex flex-col overflow-hidden">
			<p class="title text-primary">Vertical resizing - for mobile.</p>

			<div class="diff aspect-9/16 rotate-90 rounded-2xl" style:height="500px">
				<div class="diff-item-1">
					<img
						class="-rotate-90 object-contain"
						alt="Lake below Hohe Tajaköpfe"
						src="/hohe-tajakoepfe-20230709.jpg"
					/>
				</div>
				<div class="diff-item-2">
					<img
						class="-rotate-90 object-contain"
						alt="Mountain salamanders on rock"
						src="/mountain-salamander-20240702.jpg"
					/>
				</div>

				<div class="diff-resizer"></div>
			</div>
			<p class="caption text-primary-container-content mt-2 text-center text-sm">
				Switch the resizing handle to vertical double arrow
			</p>
		</div>

		<HorizontalRule />
	</div>

	{#snippet resizer(resizerStartFunction: (event: PointerEvent) => void, isActive: boolean)}
		<div
			class="resizer bg-base-200 flex h-full w-3 cursor-col-resize items-center justify-center"
			role="button"
			aria-label="Resizing panes"
			tabindex="0"
			onpointerdown={resizerStartFunction}
		>
			<div
				class="resizer-handle {isActive
					? 'bg-outline'
					: 'bg-outline-variant'} h-20 w-1 rounded-full"
			></div>
		</div>
	{/snippet}

	<div class="{prod ? 'block' : 'hidden'} col-span-2">
		<Title id="dual-panes">Dual Panes</Title>
		{@render underConstruction()}
	</div>

	<div class="{develop ? 'block' : 'hidden'} col-span-2">
		<Title id="dual-panes-dev">🚧 Dual Panes 🚧</Title>
		<div class="bg-base-200 mt-10 flex flex-col rounded-2xl">
			<div class="flex h-80 w-full p-4" bind:this={dualPaneContainer}>
				<div class="bg-primary-container/50 grow rounded-lg" style:width={dualPaneLeftWidth + 'px'}>
					Left Pane
				</div>
				{@render resizer(startResizingDualPanes, resizeDualPanesActive)}
				<div class="bg-accent-container/50 grow rounded-lg" style:width={dualPaneRightWidth + 'px'}>
					Right Pane
				</div>
			</div>
		</div>
	</div>

	<HorizontalRule />
	<!-- </div> -->

	<div class="{prod ? 'block' : 'hidden'} col-span-2">
		<Title id="triple-panes">Triple Panes</Title>
		{@render underConstruction()}
	</div>

	<div class="{develop ? 'block' : 'hidden'} col-span-2">
		<Title id="triple-panes-dev">🚧 Triple Panes 🚧</Title>
		<div class="bg-base-200 mt-10 flex flex-col rounded-2xl">
			<div class="flex h-screen w-full p-4" bind:this={triplePaneContainer}>
				<div
					class="@container/paneLeft grow-2 rounded-lg"
					bind:this={triplePaneLeftContainer}
					style:width={triplePaneLeftWidth + 'px'}
				>
					<div
						class="bg-secondary-container/50 @8xl/paneLeft:grid-cols-9 @10xl/paneLeft:grid-cols-10 grid h-full grid-cols-1 gap-4 overflow-y-scroll rounded-lg p-4 @xs/paneLeft:grid-cols-2 @sm/paneLeft:grid-cols-3 @md/paneLeft:grid-cols-4 @xl/paneLeft:grid-cols-5 @2xl/paneLeft:grid-cols-6 @4xl/paneLeft:grid-cols-7 @6xl/paneLeft:grid-cols-8"
					>
						{@render paneTile('secondary', 'A')}
						{@render paneTile('secondary', 'B')}
						{@render paneTile('secondary', 'C')}
						{@render paneTile('secondary', 'D')}
						{@render paneTile('secondary', 'E')}
						{@render paneTile('secondary', 'F')}
						{@render paneTile('secondary', 'G')}
						{@render paneTile('secondary', 'H')}
						{@render paneTile('secondary', 'I')}
						{@render paneTile('secondary', 'J')}
						{@render paneTile('secondary', 'K')}
						{@render paneTile('secondary', 'L')}
						{@render paneTile('secondary', 'M')}
						{@render paneTile('secondary', 'N')}
						{@render paneTile('secondary', 'O')}
						{@render paneTile('secondary', 'P')}
						{@render paneTile('secondary', 'Q')}
						{@render paneTile('secondary', 'R')}
						{@render paneTile('secondary', 'S')}
						{@render paneTile('secondary', 'T')}
						{@render paneTile('secondary', 'U')}
						{@render paneTile('secondary', 'V')}
						{@render paneTile('secondary', 'W')}
						{@render paneTile('secondary', 'X')}
						{@render paneTile('secondary', 'Y')}
						{@render paneTile('secondary', 'Z')}
					</div>
				</div>
				{@render resizer(startResizingLeftTriplePanes, resizeLeftTriplePanesActive)}
				<div
					class="@container/paneCenter grow-4 rounded-lg"
					bind:this={triplePaneCenterContainer}
					style:width={triplePaneCenterWidth + 'px'}
				>
					<div
						class="bg-neutral-container/50 @8xl/paneCenter:grid-cols-9 @10xl/paneCenter:grid-cols-10 grid h-full grid-cols-1 gap-4 overflow-y-scroll rounded-lg p-4 @xs/paneCenter:grid-cols-2 @sm/paneCenter:grid-cols-3 @md/paneCenter:grid-cols-4 @xl/paneCenter:grid-cols-5 @2xl/paneCenter:grid-cols-6 @4xl/paneCenter:grid-cols-7 @6xl/paneCenter:grid-cols-8"
					>
						{@render paneTile('neutral', 'A')}
						{@render paneTile('neutral', 'B')}
						{@render paneTile('neutral', 'C')}
						{@render paneTile('neutral', 'D')}
						{@render paneTile('neutral', 'E')}
						{@render paneTile('neutral', 'F')}
						{@render paneTile('neutral', 'G')}
						{@render paneTile('neutral', 'H')}
						{@render paneTile('neutral', 'I')}
						{@render paneTile('neutral', 'J')}
						{@render paneTile('neutral', 'K')}
						{@render paneTile('neutral', 'L')}
						{@render paneTile('neutral', 'M')}
						{@render paneTile('neutral', 'N')}
						{@render paneTile('neutral', 'O')}
						{@render paneTile('neutral', 'P')}
						{@render paneTile('neutral', 'Q')}
						{@render paneTile('neutral', 'R')}
						{@render paneTile('neutral', 'S')}
						{@render paneTile('neutral', 'T')}
						{@render paneTile('neutral', 'U')}
						{@render paneTile('neutral', 'V')}
						{@render paneTile('neutral', 'W')}
						{@render paneTile('neutral', 'X')}
						{@render paneTile('neutral', 'Y')}
						{@render paneTile('neutral', 'Z')}
					</div>
				</div>
				{@render resizer(startResizingRightTriplePanes, resizeRightTriplePanesActive)}
				<div
					class="bg-info-container/50 flex grow flex-wrap justify-end gap-4 overflow-y-scroll rounded-lg p-4"
					bind:this={triplePaneRightContainer}
					style:width={triplePaneRightWidth + 'px'}
				>
					{@render paneTile('info', '1')}
					{@render paneTile('info', '2')}
					{@render paneTile('info', '3')}
					{@render paneTile('info', '4')}
					{@render paneTile('info', '5')}
					{@render paneTile('info', '6')}
					{@render paneTile('info', '7')}
					{@render paneTile('info', '8')}
					{@render paneTile('info', '9')}
					{@render paneTile('info', '10')}
					{@render paneTile('info', '11')}
					{@render paneTile('info', '12')}
					{@render paneTile('info', '13')}
					{@render paneTile('info', '14')}
					{@render paneTile('info', '15')}
					{@render paneTile('info', '16')}
					{@render paneTile('info', '17')}
					{@render paneTile('info', '18')}
					{@render paneTile('info', '19')}
					{@render paneTile('info', '20')}
				</div>
			</div>
		</div>
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="triple-panes">Dynamic Panes</Title>
		{@render underConstruction()}
	</div>

	<div class="{develop ? 'block' : 'hidden'} col-span-2 mt-10">
		<Title id="dynamic-panes-dev">🚧 Dynamic Panes 🚧</Title>
		<div class="flex flex-row gap-2 p-4">
			{#if panes.some((pane) => pane.id === 'leftPane')}
				<div class="flex w-full grow flex-col gap-1">
					<button class="btn btn-success" onclick={() => closePane('leftPane')}>Close pane 1</button
					>
					<div
						class="input-filled input-success shadow-base-shadow w-full grow rounded-md shadow-inner"
					>
						<input
							type="text"
							placeholder="Data for left Pane"
							class="input input-xl"
							id="leftPaneInput"
							bind:value={dataPanes[0]}
						/>
						<label class="input-filled-label" for="leftPaneInput">Data for Left Pane:</label>
					</div>
				</div>
			{:else}
				<button class="btn btn-success" onclick={() => panes.push(leftPaneData)}>
					Open pane 1
				</button>
			{/if}
			{#if panes.some((pane) => pane.id === 'leftCenterPane')}
				<div class="flex w-full grow flex-col gap-1">
					<button class="btn btn-warning" onclick={() => closePane('leftCenterPane')}
						>Close pane 2</button
					>
					<div
						class="input-filled input-warning shadow-base-shadow w-100 grow rounded-md shadow-inner"
					>
						<input
							type="text"
							placeholder="Data for right Pane"
							class="input input-xl"
							id="rightPaneInput"
							bind:value={dataPanes[1]}
						/>
						<label class="input-filled-label" for="rightPaneInput">Data for Left Center Pane:</label
						>
					</div>
				</div>
			{:else}
				<button class="btn btn-warning" onclick={() => panes.push(leftCenterPaneData)}>
					Open pane 2
				</button>
			{/if}
			{#if panes.some((pane) => pane.id === 'rightCenterPane')}
				<div class="flex w-full grow flex-col gap-1">
					<button class="btn btn-error" onclick={() => closePane('rightCenterPane')}>
						Close pane 3
					</button>
					<div
						class="input-filled input-error shadow-base-shadow w-100 grow rounded-md shadow-inner"
					>
						<input
							type="text"
							placeholder="Data for right Center Pane"
							class="input input-xl"
							id="rightCenterPaneInput"
							bind:value={dataPanes[2]}
						/>
						<label class="input-filled-label" for="rightCenterPaneInput"
							>Data for Right Center Pane:</label
						>
					</div>
				</div>
			{:else}
				<button class="btn btn-error" onclick={() => panes.push(rightCenterPaneData)}>
					Open pane 3
				</button>
			{/if}
			{#if panes.some((pane) => pane.id === 'rightPane')}
				<div class="flex w-full grow flex-col gap-1">
					<button class="btn btn-info" onclick={() => closePane('rightPane')}>Close pane 4</button>
					<div
						class="input-filled input-info shadow-base-shadow w-100 grow rounded-md shadow-inner"
					>
						<input
							type="text"
							placeholder="Data for left Center Pane"
							class="input input-xl"
							id="leftCenterPaneInput"
							bind:value={dataPanes[3]}
						/>
						<label class="input-filled-label" for="leftCenterPaneInput">Data for Right Pane:</label>
					</div>
				</div>
			{:else}
				<button class="btn btn-info" onclick={() => panes.push(rightPaneData)}>
					Open pane 4
				</button>
			{/if}
		</div>

		<Panes panesData={panes} {closePane} />
		<HorizontalRule />
	</div>

	<div class="{prod ? 'block' : 'hidden'} col-span-2">
		<Title id="tabs">Tabs</Title>
		{@render underConstruction()}
	</div>

	<div class="{develop ? 'block' : 'hidden'} col-span-2">
		<Title id="tabs-dev">🚧 Tabs 🚧</Title>
		<p class="title text-primary mt-5">Settings from FlyonUI</p>
		<div class="bg-base-200 mt-10 rounded-xl">
			<div
				class="tabs tabs-lifted bg-base-200 shadow-outline h-full rounded-lg"
				aria-label="Tabs"
				role="tablist"
				aria-orientation="horizontal"
				{@attach initTabs}
			>
				<button
					type="button"
					class="tab active-tab:tab-active active w-full"
					id="left-tabs-lifted"
					data-tab="#left-tab-content"
					aria-controls="left-tab-content"
					role="tab"
					aria-selected="true"
				>
					Left
				</button>
				<button
					type="button"
					class="tab active-tab:tab-active w-full"
					id="center-tabs-lifted"
					data-tab="#center-tabs-content"
					aria-controls="center-tabs-content"
					role="tab"
					aria-selected="false"
				>
					Center
				</button>
				<button
					type="button"
					class="tab active-tab:tab-active w-full"
					id="right-tabs-lifted"
					data-tab="#right-tabs-content"
					aria-controls="right-tabs-content"
					role="tab"
					aria-selected="false"
				>
					Right
				</button>
			</div>

			<div class="h-100">
				<div
					id="left-tab-content"
					class="h-full overflow-scroll"
					role="tabpanel"
					aria-labelledby="left-tabs-lifted"
				>
					{@render alphabet('secondary')}
				</div>
				<div
					id="center-tabs-content"
					class="hidden h-full overflow-scroll"
					role="tabpanel"
					aria-labelledby="center-tabs-lifted"
				>
					{@render alphabet('neutral')}
				</div>
				<div
					id="right-tabs-content"
					class="hidden h-full overflow-scroll"
					role="tabpanel"
					aria-labelledby="right-tabs-lifted"
				>
					{@render alphabet('info')}
				</div>
			</div>
		</div>

		<p class="title text-primary mt-5">Color configured with Material Design</p>
		<div class="bg-base-200 mt-10 rounded-xl">
			<div
				class="tabs tabs-lifted bg-base-200 shadow-outline h-full rounded-lg"
				aria-label="Tabs styled with Material Design"
				role="tablist"
				aria-orientation="horizontal"
				{@attach initTabs}
			>
				<button
					type="button"
					class="tab active-tab:bg-accent-container active:bg-accent active w-full"
					id="left-material-tabs"
					data-tab="#left-material-tabs-content"
					aria-controls="left-material-tabs-content"
					role="tab"
					aria-selected="true"
				>
					<div class="active-tab:text-accent">Left</div>
				</button>
				<button
					type="button"
					class="tab active-tab:bg-neutral-container active:bg-neutral w-full"
					id="center-material-tabs"
					data-tab="#center-material-tabs-content"
					aria-controls="center-material-tabs-content"
					role="tab"
					aria-selected="false"
				>
					<div class="active-tab:text-neutral">Center</div>
				</button>
				<button
					type="button"
					class="tab active-tab:bg-info-container active:bg-info bg-success-container w-full"
					id="right-material-tabs"
					data-tab="#right-material-tabs-content"
					aria-controls="right-material-tabs-content"
					role="tab"
					aria-selected="false"
				>
					<div class="active-tab:text-info text-success-container-content">Right</div>
				</button>
			</div>

			<div class=" h-100">
				<div
					id="left-material-tabs-content"
					class="h-full overflow-scroll"
					role="tabpanel"
					aria-labelledby="left-material-tabs"
				>
					{@render alphabet('accent')}
				</div>
				<div
					id="center-material-tabs-content"
					class="hidden h-full overflow-scroll"
					role="tabpanel"
					aria-labelledby="center-material-tabs"
				>
					{@render alphabet('neutral')}
				</div>
				<div
					id="right-material-tabs-content"
					class="hidden h-full overflow-scroll"
					role="tabpanel"
					aria-labelledby="right-material-tabs"
				>
					{@render alphabet('info')}
				</div>
			</div>
		</div>
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="modals">Modals</Title>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Title id="modals-dev">🚧 Modals 🚧</Title>
		<button
			type="button"
			class="btn btn-accent"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="basic-modal"
			data-overlay="#basic-modal"
		>
			Open modal
		</button>

		<!--
		removed from button: 
		onclick={openModal}
		removed from div class="overlay modal":
		bind:this={myModal}
		-->

		<!-- <div bind:this={modal} id="basic-modal" class="overlay modal overlay-open:opacity-100 hidden" role="dialog" tabindex="-1"> -->
		<div
			id="basic-modal"
			class="overlay modal overlay-open:opacity-100 hidden"
			role="dialog"
			tabindex="-1"
			{@attach initOverlay}
		>
			<div class="modal-dialog overlay-open:opacity-100">
				<div class="modal-content bg-base-300">
					<div class="modal-header">
						<h3 class="modal-title">First Dialog Title</h3>
						<button
							type="button"
							class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
							aria-label="Close"
							data-overlay="#basic-modal"
						>
							<span class="icon-[tabler--x] size-4"></span>
						</button>
					</div>
					<div class="modal-body">
						This is some placeholder content to show the scrolling behavior for modals. Instead of
						repeating the text in the modal, we use an inline style to set a minimum height, thereby
						extending the length of the overall modal and demonstrating the overflow scrolling. When
						content becomes longer than the height of the viewport, scrolling will move the modal as
						needed.
					</div>
					<div class="modal-footer">
						<button type="button" class="btn btn-secondary btn-soft" data-overlay="#basic-modal"
							>Close</button
						>
						<button type="button" class="btn btn-primary">Save changes</button>
					</div>
				</div>
			</div>
		</div>

		<button
			type="button"
			class="btn btn-primary"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="centered-modal"
			data-overlay="#centered-modal"
		>
			Open centered modal
		</button>

		<div
			id="centered-modal"
			class="overlay modal modal-middle overlay-open:opacity-100 hidden"
			role="dialog"
			tabindex="-1"
		>
			<div class="modal-dialog overlay-open:opacity-100">
				<div class="modal-content bg-base-300">
					<div class="modal-header">
						<h3 class="modal-title">Centered Dialog Title</h3>
						<button
							type="button"
							class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
							aria-label="Close"
							data-overlay="#centered-modal"
						>
							<span class="icon-[tabler--x] size-4"></span>
						</button>
					</div>
					<div class="modal-body">
						This is some placeholder content to show the scrolling behavior for modals. Instead of
						repeating the text in the modal, we use an inline style to set a minimum height, thereby
						extending the length of the overall modal and demonstrating the overflow scrolling. When
						content becomes longer than the height of the viewport, scrolling will move the modal as
						needed.
					</div>
					<div class="modal-footer">
						<button type="button" class="btn btn-secondary btn-soft" data-overlay="#centered-modal"
							>Close</button
						>
						<button type="button" class="btn btn-primary">Save changes</button>
					</div>
				</div>
			</div>
		</div>

		<button
			type="button"
			class="btn btn-primary"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="share-modal"
			data-overlay="#share-modal"
		>
			Open share modal
		</button>

		<div
			id="share-modal"
			class="overlay modal modal-middle overlay-open:opacity-100 hidden"
			role="dialog"
			tabindex="-1"
		>
			<div class="modal-dialog overlay-open:opacity-100">
				<div class="modal-content bg-base-300 shadow-outline shadow-xl">
					<div class="modal-header">
						<h3 class="modal-title">Share</h3>
						<button
							type="button"
							class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
							aria-label="Close"
							data-overlay="#share-modal"
						>
							<span class="icon-[tabler--x] size-4"></span>
						</button>
					</div>
					<div class="modal-body">
						<div class="w-full overflow-x-auto">
							TBD: add dropdown for selecting new groups here<br />
							TBD: add a heading for the table: existing permissions<br />
							TBD: make existing permissions clickable / editable with dropdowns on click and add delete
							button<br />
							<table class="table shadow-inner">
								<thead>
									<tr>
										<th>Group</th>
										<th>Rights</th>
									</tr>
								</thead>
								<tbody>
									<tr>
										<td class="text-nowrap">First group's name here </td>
										<td class="text-center"><span class="icon-[tabler--eye]"></span></td>
									</tr>
									<tr>
										<td class="text-nowrap">Another groups name comes here </td>
										<td class="text-center"><span class="icon-[tabler--eye]"></span></td>
									</tr>
									<tr>
										<td class="text-nowrap">And one more groups name here, so group3 </td>
										<td class="text-center"
											><span class="icon-[material-symbols--edit-outline-rounded]"></span></td
										>
									</tr>
									<tr>
										<td class="text-nowrap">Group 4</td>
										<td class="text-center"><span class="icon-[tabler--key-filled]"></span></td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>
					<div class="modal-footer">
						<button type="button" class="btn btn-secondary btn-soft" data-overlay="#share-modal"
							>Close</button
						>
						<button type="button" class="btn btn-primary">Save changes</button>
					</div>
				</div>
			</div>
		</div>

		<button
			type="button"
			class="btn btn-warning"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="add-element-modal"
			data-overlay="#add-element-modal"
		>
			<span class="icon-[material-symbols--edit-outline-rounded]"></span>
			Create new element
		</button>

		<div
			id="add-element-modal"
			class="overlay modal modal-middle overlay-open:opacity-100 hidden"
			role="dialog"
			tabindex="-1"
		>
			<div class="modal-dialog overlay-open:opacity-100">
				<div class="modal-content bg-base-300 shadow-outline shadow">
					<div class="modal-header">
						<h3 class="modal-title">Add an Element</h3>
						<button
							type="button"
							class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
							aria-label="Close"
							data-overlay="#add-element-modal"
						>
							<span class="icon-[tabler--x] size-4"></span>
						</button>
					</div>
					<div class="modal-body">
						<div class="w-full overflow-x-auto">
							<div class="input-filled input-base-content mb-2 w-fit grow">
								<input
									type="text"
									placeholder="Name the demo resource"
									class="input input-sm md:input-md shadow-shadow shadow-inner"
									id="name_id_new_element"
									name="name"
								/>
								<label class="input-filled-label" for="name_id_new_element">Name</label>
							</div>
							<div class="textarea-filled textarea-base-content w-full">
								<textarea
									class="textarea shadow-shadow shadow-inner"
									placeholder="Describe the demo resource here."
									id="description_id_new_element"
									name="description"
								>
								</textarea>
								<label class="textarea-filled-label" for="description_id_new_element">
									Description
								</label>
							</div>
						</div>
					</div>
					<div class="modal-footer">
						<button
							class="btn-warning-container btn btn-circle btn-gradient"
							aria-label="Send Icon Button"
						>
							<span class="icon-[tabler--send-2]"></span>
						</button>
					</div>
				</div>
			</div>
		</div>

		<HorizontalRule />
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Title id="drawer">Drawer (Sidebar)</Title>
		{@render underConstruction()}
	</div>

	<!-- This local override works:
		style="background-color: var(--my-color); color: var(--md-sys-color-on-primary);" -->
	<div class={develop ? 'block' : 'hidden'}>
		<Title id="drawer-dev">🚧 Drawer (Sidebar) 🚧</Title>
		<button
			type="button"
			class="btn btn-primary"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="overlay-example"
			data-overlay="#overlay-example">Open drawer</button
		>

		<div
			id="overlay-example"
			class="overlay drawer drawer-start overlay-open:translate-x-0 hidden"
			role="dialog"
			tabindex="-1"
		>
			<div class="drawer-header">
				<h3 class="drawer-title">Drawer Title</h3>
				<button
					type="button"
					class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
					aria-label="Close"
					data-overlay="#overlay-example"
				>
					<span class="icon-[tabler--x] size-5"></span>
				</button>
			</div>
			<div class="drawer-body">
				<p>
					Some text as placeholder. In real life you can have the elements you have chosen. Like,
					text, images, lists, etc.
				</p>
			</div>
			<div class="drawer-footer">
				<button type="button" class="btn btn-secondary btn-soft" data-overlay="#overlay-example"
					>Close</button
				>
				<button type="button" class="btn btn-primary">Save changes</button>
			</div>
		</div>

		<HorizontalRule />
	</div>
</div>

<style>
	.custom-select {
		&,
		&::picker(select) {
			appearance: base-select;
		}
		/* :open::picker-icon {
			rotate: 180deg;
		}
		::picker-icon {
			color: var(--md-sys-color-primary);
			transition: 0.4s rotate;
		} */
	}
	.resizer:hover .resizer-handle {
		background: var(--md-sys-color-outline);
	}
	/* Prevent touch scrolling from hijacking drags on mobile */
	.resizer,
	.resizer-handle {
		touch-action: none;
	}
	/* select:open::picker-icon {
		rotate: 180deg;
	}
	select::picker-icon {
		color: var(--md-sys-color-primary);
		transition: 0.4s rotate;
	} */
</style>
