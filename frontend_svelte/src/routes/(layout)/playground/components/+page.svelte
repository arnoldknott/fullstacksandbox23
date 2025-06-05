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
	import { enhance } from '$app/forms';
	import ShareItem from './ShareItem.svelte';
	// import type { PageProps } from '../$types';
	import { page } from '$app/state';
	import type { ActionResult } from '@sveltejs/kit';
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
			const team = teams.find((team) => team.id === result.data?.identityId);
			if (team) {
				team.right = result.data?.confirmedNewAction
					? result.data.confirmedNewAction.toString()
					: '';
			}
		} else {
			// handle error: show error message
		}
		update();
	};

	// data for share menu:
	const teams = $state(
		[
			{
				id: '1',
				name: 'The A Team',
				right: 'read'
			},
			{
				id: '2',
				name: 'Awesome Team',
				right: ''
			},
			{
				id: '3',
				name: 'Team Teams',
				right: 'write'
			},
			{
				id: '4',
				name: 'Team Next',
				right: 'own'
			},
			{
				id: '5',
				name: 'Be a Team',
				right: 'read'
			},
			{
				id: '6',
				name: 'Very long Team Name',
				right: 'write'
			}
		].sort((a, b) => a.name.localeCompare(b.name))
	);

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

	// for theme picker:
	let sourceColor = $state('#769CDF');
	let variant = $state('TONAL_SPOT');
	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
	const allContrasts = Array.from(
		{ length: (contrastMax - contrastMin) / contrastStep + 1 },
		(_, i) => contrastMin + i * contrastStep
	);
	let contrast = $state(0.0);

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
					class="bg-base-200 shadow-outline max-h-96 min-h-44 overflow-y-auto rounded-lg p-2 shadow-inner"
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
					class="bg-base-200 shadow-outline max-h-96 min-h-44 overflow-y-auto rounded-lg p-2 shadow-inner"
				>
					Some text
				</div>
			</Card>
		</div>
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
								{#each teams as team, i (i)}
									<ShareItem resourceId="actionButtonShareResourceId" icon="icon-[fluent--people-team-16-filled]" identity={team} />
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
								{#each teams as team, i (i)}
									<ShareItem resourceId="dropdownShareDropdownResourceId" icon="icon-[fluent--people-team-16-filled]" identity={team} />
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
							<ShareItem resourceId="dropdownShareResourceId" icon="icon-[fluent--people-team-16-filled]" identity={teams[0]} />
						</form>
					</ul>
				</div>
			</div>
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
	</div>

	<div class={prod ? 'block' : 'hidden'}>
		<Heading>Theme Picker</Heading>
		{@render underConstruction()}
	</div>

	<div class={develop ? 'block' : 'hidden'}>
		<Heading>🚧 Theme Picker 🚧</Heading>
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
					bind:value={sourceColor}
				/>
			</div>
			<div class="relative w-48">
				<label class="label label-text" for="themeVariant">Variant</label>
				<select
					class="select select-floating max-w-sm"
					aria-label="Select variant"
					id="themeVariant"
					bind:value={variant}
				>
					<option value="TONAL_SPOT">Tonal Spot</option>
					<option value="MONOCHROME">Monochrome</option>
					<option value="NEUTRAL">Neutral</option>
					<option value="VIBRANT">Vibrant</option>
					<option value="EXPRESSIVE">Expressive</option>
					<option value="FIDELITY">Fidelity</option>
					<option value="CONTENT">Content</option>
					<option value="RAINBOW">Rainbow</option>
					<option value="FRUIT_SALAD">Fruit Salad</option>
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
					bind:value={contrast}
				/>
				<div class="flex w-full justify-between px-2 text-xs">
					{#each allContrasts as _ (_)}
						<span>|</span>
					{/each}
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
							data-overlay="#basic-modal"
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
