<script lang="ts">
	import { themeStore } from '$lib/stores';
	import type { AppTheme } from '$lib/theming';
	import { Hct, hexFromArgb } from '@material/material-color-utilities';
	import { onDestroy } from 'svelte';
	import Heading from '$components/Heading.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import NavigationCard from '$components/NavigationCard.svelte';
	// import type { IOverlay } from 'flyonui/flyonui';
	// import { HSDropdown, type IHTMLElementPopper } from 'flyonui/flyonui';
	// import type { IHTMLElementPopper, HSDropdown } from 'flyonui/flyonui';
	import type { IHTMLElementFloatingUI, HSDropdown } from 'flyonui/flyonui';
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
	import { Action, AccessHandler, IdentityType } from '$lib/accessHandler';
	import type { AccessShareOption } from '$lib/types';
	import ThemePicker from './ThemePicker.svelte';
	import ArtificialIntelligencePicker from './ArtificialIntelligencePicker.svelte';
	import { Model, type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
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
	// let dropdownMenu = $state<HTMLUListElement | undefined>(undefined);
	let actionButtonShareMenuElement = $state<HTMLElement | undefined>(undefined);
	let dropdownShareDropdownElement = $state<HTMLElement | undefined>(undefined);
	let dropdownMenuElement = $state<HTMLElement | undefined>(undefined);
	let dropdownShareElement = $state<HTMLElement | undefined>(undefined);
	// let dropdownMenuElement = $state<HTMLElement | undefined>(undefined);
	let actionButtonShareMenu = $state<HSDropdown | undefined>(undefined);
	let dropdownShareDropdown = $state<HSDropdown | undefined>(undefined);
	let dropdownMenu = $state<HSDropdown | undefined>(undefined);
	let dropdownShare = $state<HSDropdown | undefined>(undefined);

	const loadHSDropdown = async () => {
		const { HSDropdown } = await import('flyonui/flyonui');
		return HSDropdown;
	};

	// // TBD: is this stopping the dropdown from stalling? No, it doesn't, but the issue only exists in development mode.
	// window.HSStaticMethods.autoInit(["dropdown"]);

	// TBD: make sure all dropdowns close and get reset, when user does not click any of the list items, but elsewhere on the screen.
	// use the event from the main dropdown to listen and close the child dropdowns.
	// const closeChildDropdowns: Attachment = () => {
	// 	dropdownMenu?.on("close", dropdownShareDropdown?.close());
	// TBD: potentially using {@attach} for this?

	$effect(() => {
		// afterNavigate(() => {
		loadHSDropdown().then((LoadedHSDropdown) => {
			dropdownMenu = new LoadedHSDropdown(dropdownMenuElement as unknown as IHTMLElementFloatingUI);
			dropdownShareDropdown = new LoadedHSDropdown(
				dropdownShareDropdownElement as unknown as IHTMLElementFloatingUI
			);
			actionButtonShareMenu = new LoadedHSDropdown(
				actionButtonShareMenuElement as unknown as IHTMLElementFloatingUI
			);
			dropdownShare = new LoadedHSDropdown(
				dropdownShareElement as unknown as IHTMLElementFloatingUI
			);
			// });
		});
	});

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
				action: undefined
			},
			{
				identity_id: '3',
				identity_name: 'Ueber Group',
				identity_type: IdentityType.UEBER_GROUP,
				action: Action.WRITE
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

	let selectedAction: Action | undefined = $state(Action.READ);

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

	// // for modal and drawer:
	// const loadHSOverlay = async () => {
	// 	const { HSOverlay } = await import('flyonui/flyonui.js');
	// 	return HSOverlay;
	// };

	// let myModal: HTMLElement;
	// let overlay: IOverlay | undefined = $state();

	// $effect(() => {
	// 	loadHSOverlay().then((loadHSOverlay) => {
	// 		overlay = new loadHSOverlay(myModal);
	// 	});
	// });

	// const openModal = () => {
	// 	overlay?.open();
	// };
</script>

<!-- <svelte:window use:mapDropdown /> -->

<div class="flex flex-row justify-around">
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
		<Heading>Card with chat</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Card with chat 🚧</Heading>
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
		<Heading>Card with text and title navigation</Heading>
		<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
			{#each cardsNavigation as cardNavigation, i (i)}
				<NavigationCard title={cardNavigation.title} href={cardNavigation.link}
					>{cardNavigation.description}</NavigationCard
				>
			{/each}
		</div>
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Card with text and title navigation 🚧</Heading>
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
		<Heading>Card with dropdown menu</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Card with dropdown menu 🚧</Heading>
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
		<Heading>Card with action buttons</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Card with action buttons 🚧</Heading>
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
					<!-- Add to class [--auto-close:inside] 
					 after refactoring into select menu -->
					<div
						class="dropdown join-item relative inline-flex grow [--placement:top]"
						bind:this={actionButtonShareMenuElement}
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
							<form
								method="POST"
								name="actionButtonShareForm"
								use:enhance={async () => {
									actionButtonShareMenu?.close();
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
		<Heading>Buttons</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Buttons 🚧</Heading>
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
		<Heading>Dropdown menus</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Dropdown menus 🚧</Heading>
		<div class="mb-20 flex flex-wrap gap-4">
			<div
				class="dropdown relative inline-flex rtl:[--placement:bottom-end]"
				bind:this={dropdownMenuElement}
			>
				<!-- {@attach closeChildDropdowns()} -->
				<!-- onload={async()=> await  loadHSDropdown()} -->
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
					<!-- Add to class [--auto-close:inside] 
					 after refactoring into select menu -->
					<li
						class="dropdown relative items-center [--offset:15] [--placement:right-start] max-sm:[--placement:bottom-start]"
						bind:this={dropdownShareDropdownElement}
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
							<form
								method="POST"
								name="dropDownShareDropdownForm"
								use:enhance={async () => {
									dropdownMenu?.close();
									dropdownShareDropdown?.close();
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
				<!-- Add to class [--auto-close:inside]
					 after refactoring into select menu -->
				<div class="dropdown relative inline-flex" bind:this={dropdownShareElement}>
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
						<form
							method="POST"
							name="dropdownShareForm"
							use:enhance={async () => {
								dropdownShare?.close();
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
		<Heading>Selections</Heading>
		{@render underConstruction()}
	</div>

	{#snippet shareSelect(right: Action | undefined)}
		{#if browser === 'Firefox' || browser === 'Safari'}
			<!-- {right || 'none'} -->
		{:else}
			<span class={AccessHandler.rightsIcon(right)}></span>
		{/if}
	{/snippet}
	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Selections 🚧</Heading>
		<div class="bg-base-300 mb-20 flex flex-wrap gap-4">
			<!-- <div> -->
			<!-- <label class="label label-text" for="right-selector" -->
			<span class="{AccessHandler.rightsIcon(selectedAction)} size-6"></span>
			<div class="">
				<form class=" w-17">
					<!-- <label for="rights"><span class={AccessHandler.rightsIcon(selectedAction)}></span></label> -->
					<select
						class="custom-select bg-base-300 w-full pr-3"
						id="rights"
						aria-label="Select rights"
						bind:value={selectedAction}
					>
						<!-- <button>
							<selectedcontent></selectedcontent>
						</button> -->

						<!-- <option value="">Please select a pet</option> -->
						<!-- TBD: add emojis as alternative for older browsers! -->
						<option
							class="dropdown-item dropdown-close bg-base-300 text-success"
							value={Action.OWN}
						>
							{@render shareSelect(Action.OWN)} own
						</option>
						<option
							class="dropdown-item dropdown-close bg-base-300 text-warning"
							value={Action.WRITE}
						>
							{@render shareSelect(Action.WRITE)} write
						</option>
						<option
							class="dropdown-item dropdown-close bg-base-300 text-neutral"
							value={Action.READ}
						>
							{@render shareSelect(Action.READ)} read
						</option>
						<option class="dropdown-item dropdown-close bg-base-300 text-error" value={undefined}>
							{@render shareSelect(undefined)} none
						</option>
					</select>
				</form>
			</div>
			<!-- <select
				class="select select-floating max-w-sm"
				aria-label="Select right"
				id="rights-{shareOption.identity_id}"
				name="right-selector"
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
		<Heading>Status sliders with Hue-Chroma-Tone</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Status sliders with Hue-Chroma-Tone 🚧</Heading>
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
		<Heading>Tooltips</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Tooltips 🚧</Heading>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div class="tooltip">
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
		<Heading>Theme Picker</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Theme Picker 🚧</Heading>
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
		<Heading>Caroussels</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Caroussels 🚧</Heading>
		<!-- TBD: pass those data-carousel arguments:
		 " '{' "loadingClasses": "opacity-0" '}'" -->
		<div id="vertical-thumbnails" data-carousel class="relative w-full">
			<div class="carousel flex space-x-2 rounded-none">
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
		<Heading>Vertical Tabs</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Vertical Tabs 🚧</Heading>
		<div class="flex">
			<div
				class="tabs tabs-bordered tabs-vertical w-[130px]"
				aria-label="Tabs"
				role="tablist"
				data-tabs-vertical="true"
				aria-orientation="horizontal"
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
							<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
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

	<div class={prod ? 'block' : 'hidden'}>
		<Heading>Modals</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Modals 🚧</Heading>
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
		<Heading>Drawer (Sidebar)</Heading>
		{@render underConstruction()}
	</div>

	<!-- This local override works:
		style="background-color: var(--my-color); color: var(--md-sys-color-on-primary);" -->
	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Drawer (Sidebar) 🚧</Heading>
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
	}
	select:open::picker-icon {
		rotate: 180deg;
	}
	select::picker-icon {
		color: var(--md-sys-color-primary);
		transition: 0.4s rotate;
	}
</style>
