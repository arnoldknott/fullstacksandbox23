<script lang="ts">
	import { themeStore } from '$lib/stores';
	import type { AppTheme } from '$lib/theming';
	import { Hct, hexFromArgb } from '@material/material-color-utilities';
	import { onDestroy } from 'svelte';
	import Heading from '$components/Heading.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	// import type { IOverlay } from 'flyonui/flyonui';
	// import { HSDropdown, type IHTMLElementPopper } from 'flyonui/flyonui';
	// import type { IHTMLElementPopper, HSDropdown } from 'flyonui/flyonui';
	import type { IHTMLElementFloatingUI, HSDropdown } from 'flyonui/flyonui';
	// import { afterNavigate } from '$app/navigation';
	import Card from '$components/Card.svelte';

	// for dropdown menus:
	// let dropdownMenu = $state<HTMLUListElement | null>(null);
	let dropdownElement = $state<HTMLElement | null>(null);
	// let dropdownMenuElement = $state<HTMLElement | null>(null);
	let dropdown = $state<HSDropdown | null>(null);

	const loadHSDropdown = async () => {
		const { HSDropdown } = await import('flyonui/flyonui');
		return HSDropdown;
	};

	// const loadHSDropdown = async () => {
	// 	const { HSDropdown } = await import('flyonui/flyonui');
	// 	console.log('components - page - loadHSDropdown - HSDropdown')
	// 	console.log(HSDropdown)
	// 	dropdown = new HSDropdown(dropdownElement as unknown as IHTMLElementPopper);
	// };
	// const mapDropdown = (_node: HTMLElement) => {
	// 	afterNavigate( () => {
	// 		console.log('components - page - mapDrowdown - afterNavigate')
	// 		// loadHSDropdown().then((LoadedHSDropdown) => {
	// 		// 	dropdownMenu = new LoadedHSDropdown(dropdownMenuElement);
	// 		// })
	// 	})
	// };
	// let dropdownMenu = $derived.by(async () => {
	// 	if (dropdownMenuElement){
	// 		const { HSDropdown } = await import('flyonui/flyonui');
	// 		return new HSDropdown(dropdownMenuElement as unknown as IHTMLElementPopper)
	// 	}});

	$effect(() => {
		// afterNavigate(() => {
		// console.log('components - page - $effect - dropdown')
		// console.log(dropdownElement)
		loadHSDropdown().then((LoadedHSDropdown) => {
			// console.log("=== component - LoadedHSDropdown ===")
			// console.log(LoadedHSDropdown)
			// dropdown = new LoadedHSDropdown(dropdownElement as unknown as IHTMLElementPopper);
			dropdown = new LoadedHSDropdown(dropdownElement as unknown as IHTMLElementFloatingUI);
			// dropdownMenu
			// console.log("=== dropdownMenu ===")
			// console.log(dropdownMenu)
		});
		// })
		// if (dropdownElement) {
		//     (async () => {
		//         try {
		//             const LoadedHSDropdown = await loadHSDropdown();
		//             // Ensure the dropdown is not already initialized
		//             if (!dropdown) {
		//                 dropdown = new LoadedHSDropdown(dropdownElement as unknown as IHTMLElementPopper);
		//             }
		//         } catch (error) {
		//             console.error('Error initializing dropdown:', error);
		//         }
		//     })();
		// }
	});

	const teams = $state([
		{
			name: 'The A Team',
			right: 'read'
		},
		{
			name: 'Awesome Team',
			right: ''
		},
		{
			name: 'Team Teams',
			right: 'write'
		},
		{
			name: 'Team Next',
			right: 'own'
		},
		{
			name: 'Be a Team',
			right: 'read'
		}
	]);
	const rightsIcon = (right: string) => {
		return right === 'own'
			? 'icon-[tabler--key-filled] bg-success'
			: right === 'write'
				? 'icon-[material-symbols--edit-outline-rounded] bg-warning'
				: right === 'read'
					? 'icon-[tabler--eye] bg-neutral'
					: 'icon-[tabler--ban] bg-error';
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

<div class="w-full xl:grid xl:grid-cols-2 xl:gap-4">
	<div>
		<Heading>Card with chat</Heading>
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
						aria-label="Add Icon Button"
					>
						<span class="icon-[tabler--send-2]"></span>
					</button>
				</div>
			{/snippet}
		</div>
	</div>

	<div>
		<Heading>Card with text and navigation</Heading>
		<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
			<div
				class="card border-outline-variant bg-base-250 shadow-outline-variant rounded-xl border-[1px] shadow-lg"
			>
				<div class="card-header">
					<h5 class="title-small md:title lg:title-large base-content card-title">
						Here's a title
					</h5>
				</div>
				<div class="card-body">
					<p class="body-small md:body text-primary-container-content">
						Some test text, here. Can go over several lines. And if it does, the cards in the same
						line will adjust to the longest card. This is a good way to keep the layout clean and
						consistent.
					</p>
				</div>
				<div class="card-footer">
					<div class="card-actions text-center">
						<a href="#top"
							><button
								class="label-small btn btn-primary text-primary-content shadow-primary rounded-full px-3"
								>Link to top of page</button
							></a
						>
					</div>
				</div>
			</div>
			<div
				class="card border-outline-variant bg-base-250 shadow-outline-variant rounded-xl border-[1px] shadow-lg"
			>
				<div class="card-header">
					<h5 class="title-small md:title lg:title-large base-content card-title">
						One more title
					</h5>
				</div>
				<div class="card-body">
					<p class="body-small md:body text-primary-container-content">
						Some shorter text here - but adjusts to the height of the neigour card
					</p>
				</div>
				<div class="card-footer">
					<div class="card-actions text-center">
						<a href="#top"
							><button
								class="label-small btn btn-primary text-primary-content shadow-primary rounded-full px-3"
								>Link to top of page</button
							></a
						>
					</div>
				</div>
			</div>
			<div
				class="card border-outline-variant bg-base-250 shadow-outline-variant rounded-xl border-[1px] shadow-lg"
			>
				<div class="card-header">
					<h5 class="title-small md:title lg:title-large base-content card-title">A third title</h5>
				</div>
				<div class="card-body">
					<p class="body-small md:body text-primary-container-content">
						This one is meant to fill the row. Note how the cards are responsive on smaller screens.
					</p>
				</div>
				<div class="card-footer">
					<div class="card-actions text-center">
						<a href="#top"
							><button
								class="label-small btn btn-primary text-primary-content shadow-primary rounded-full px-3"
								>Link to top of page</button
							></a
						>
					</div>
				</div>
			</div>
		</div>
	</div>

	<div>
		<Heading>Card with edits</Heading>
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
							<!-- <button id="dropdown-menu-icon" type="button" class="dropdown-toggle btn btn-square btn-text btn-secondary" aria-haspopup="menu" aria-expanded="false" aria-label="Dropdown">
								<span class="icon-[tabler--dots-vertical] size-6"></span>
							</button> -->
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

	<div>
		<Heading>Dropdown menus</Heading>
		<div
			class="dropdown relative inline-flex rtl:[--placement:bottom-end]"
			bind:this={dropdownElement}
		>
			<!-- onload={async()=> await  loadHSDropdown()} -->
			<span
				id="dropdown-menu-icon"
				class="dropdown-toggle icon-[tabler--dots-vertical] text-secondary size-6"
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
				<li class="items-center">
					<button
						class="btn dropdown-item btn-text text-secondary content-center justify-start"
						aria-label="Edit Button"
						onclick={() => (edit ? (edit = false) : (edit = true))}
						><span class="icon-[material-symbols--edit-outline-rounded]"></span> Edit</button
					>
				</li>
				<li
					class="dropdown relative items-center [--offset:15] [--placement:right-start] max-sm:[--placement:bottom-start]"
				>
					<button
						id="share"
						class="dropdown-toggle btn dropdown-item btn-text text-secondary content-center justify-start"
						aria-haspopup="menu"
						aria-expanded="false"
						aria-label="Share with"
						><span class="icon-[tabler--share-2]"></span>Share
						<span class="icon-[tabler--chevron-right] size-4 rtl:rotate-180"></span>
					</button>
					<!-- min-w-60 -->
					<ul
						class="dropdown-menu bg-base-300 shadow-outline dropdown-open:opacity-100 hidden min-w-[15rem] shadow-xs"
						role="menu"
						aria-orientation="vertical"
						aria-labelledby="share"
					>
						<li>
							<div class="text-secondary flex items-center">
								<div class="dropdown-item text-secondary max-w-40 content-center">
									<span class="icon-[fluent--people-team-16-filled]"></span>{teams[0].name}
								</div>
								<div class="mr-2">
									<!-- {rightsIconSelection(team.id) ? "bg-success" : ""} -->
									<span class="{rightsIcon(teams[0].right)} size-4"></span>
								</div>
								<div
									class="dropdown bg-base-300 relative inline-flex [--offset:0] [--placement:left-start]"
								>
									<ul
										class="dropdown-menu bg-base-300 outline-outline dropdown-open:opacity-100 hidden outline-2"
										role="menu"
										aria-orientation="vertical"
										aria-labelledby="rights"
									>
										<li>
											<!-- The teamRight assignment needs to turn into a form submission, calling share() / createOrUpdateAccessPolicy()
									combine with an accessPolicyExists - that also indicates the user, wether this policy already exists through a checkmark  -->
											<button
												data-sveltekit-preload-data={false}
												class="btn dropdown-item btn-text max-w-40 content-center"
												name="id"
												type="submit"
												onclick={() => {
													teams[0].right = 'own';
													dropdown?.close();
												}}
												aria-label="own"
												><span class="icon-[tabler--key-filled] bg-success"></span></button
											>
										</li>
										<li>
											<button
												data-sveltekit-preload-data={false}
												class="btn dropdown-item btn-text max-w-40 content-center"
												name="id"
												type="submit"
												onclick={() => {
													teams[0].right = 'write';
													dropdown?.close();
												}}
												aria-label="write"
												><span class="icon-[material-symbols--edit-outline-rounded] bg-warning"
												></span>
											</button>
										</li>
										<li>
											<button
												data-sveltekit-preload-data={false}
												class="btn dropdown-item btn-text max-w-40 content-center"
												name="id"
												type="submit"
												onclick={() => {
													teams[0].right = 'read';
													dropdown?.close();
												}}
												aria-label="read"
												><span class="icon-[tabler--eye] bg-neutral"></span>
											</button>
										</li>
										<li>
											<button
												data-sveltekit-preload-data={false}
												class="btn dropdown-item btn-text max-w-40 content-center"
												name="id"
												type="submit"
												onclick={() => {
													teams[0].right = '';
													dropdown?.close();
												}}
												aria-label="remove share"
												><span class="icon-[tabler--ban] bg-error"></span>
											</button>
										</li>
									</ul>
									<button
										id="rights"
										type="button"
										class="dropdown-toggle btn btn-text bg-base-300"
										aria-haspopup="menu"
										aria-expanded="false"
										aria-label="Dropdown"
									>
										<span class="icon-[tabler--chevron-down] dropdown-open:rotate-180 size-4"
										></span>
									</button>
								</div>
								<!-- <div class={rightsIconSelection(team.id) ? 'block' : 'invisible'}>
									<span class="icon-[openmoji--check-mark]"></span>
								</div> -->
							</div>
						</li>
						<li class="dropdown-footer gap-2">
							<button class="btn dropdown-item btn-text text-secondary content-center justify-start"
								>... more options</button
							>
						</li>
					</ul>
				</li>
				<li class="dropdown-footer gap-2">
					<button
						class="btn dropdown-item btn-error btn-text content-center justify-start"
						aria-label="Delete Button"
						name="id"
						formaction="?/delete"><span class="icon-[tabler--trash]"></span>Delete</button
					>
				</li>
			</ul>
		</div>
	</div>

	<div>
		<Heading>Inputs</Heading>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="input-filled w-full grow">
				<input type="text" placeholder="Primary colored input" class="input" id="filledInput" />
				<label class="input-filled-label" for="filledInput">Full name</label>
			</div>
			<div class="input-filled input-secondary w-full grow">
				<input
					type="text"
					placeholder="Secondary colored input"
					class="input border-secondary"
					id="filledInputSecondary"
				/>
				<label class="input-filled-label text-secondary" for="filledInputSecondary">Full name</label
				>
			</div>
			<div class="input-filled input-accent w-full grow">
				<input
					type="text"
					placeholder="Accent colored input"
					class="input"
					id="filledInputAccent"
				/>
				<label class="input-filled-label" for="filledInputAccent">Full name</label>
			</div>
			<div class="input-filled input-neutral w-full grow">
				<input
					type="text"
					placeholder="Neutral colored input"
					class="input"
					id="filledInputNeutral"
				/>
				<label class="input-filled-label" for="filledInputNeutral">Full name</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="input-filled w-full grow">
				<input type="text" placeholder="John Doe" class="input" id="filledInputDisabled" disabled />
				<label class="input-filled-label" for="filledInputDisabled">Full name - disabled</label>
			</div>
			<div class="input-filled w-full grow">
				<input type="text" placeholder="John Doe" class="input is-valid" id="filledInputIsValid" />
				<label class="input-filled-label" for="filledInputIsValid">Full name - is-valid</label>
			</div>
			<div class="input-filled w-full grow">
				<input
					type="text"
					placeholder="John Doe"
					class="input is-invalid"
					id="filledInputIsInvalid"
				/>
				<label class="input-filled-label" for="filledInputIsInvalid">Full name - is-invalid</label>
			</div>
			<div class="input-floating w-full grow">
				<input type="text" placeholder="John Doe" class="input" id="floatingInput" />
				<label class="input-floating-label" for="floatingInput">Full name - floating</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-xs" id="filledInputXs" />
				<label class="input-filled-label" for="filledInputXs">Full name - xs</label>
			</div>
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-sm" id="filledInputSm" />
				<label class="input-filled-label" for="filledInputSm">Full name - sm</label>
			</div>
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-md" id="filledInputDefault" />
				<label class="input-filled-label" for="filledInputDefault">Full name - default</label>
			</div>
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-lg" id="filledInputLg" />
				<label class="input-filled-label" for="filledInputLg">Full name - lg</label>
			</div>
			<div class="input-filled w-full">
				<input type="text" placeholder="John Doe" class="input input-xl" id="filledInputXl" />
				<label class="input-filled-label" for="filledInputXl">Full name - xl</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="input-filled w-full grow">
				<input
					type="text"
					placeholder="John Doe"
					class="input input-xs sm:input-sm md:input-md lg:input-lg xl:input-xl"
					id="filledInputResponsive"
				/>
				<label class="input-filled-label" for="filledInputResponsive">Full name - responsive</label>
			</div>
			<div class="input-floating w-full grow">
				<input
					type="text"
					placeholder="John Doe"
					class="input input-xs sm:input-sm md:input-md lg:input-lg xl:input-xl"
					id="filledInputResponsive"
				/>
				<label class="input-floating-label" for="filledInputResponsive"
					>Full name - responsive</label
				>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="textarea-filled w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledPrimary"></textarea>
				<label class="textarea-filled-label" for="textareaFilledPrimary">Your bio</label>
			</div>
			<div class="textarea-filled textarea-secondary w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledSecondary"></textarea>
				<label class="textarea-filled-label" for="textareaFlilledSecondary">Your bio</label>
			</div>
			<div class="textarea-filled textarea-accent w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledAccent"></textarea>
				<label class="textarea-filled-label" for="textareaFilledAccent">Your bio</label>
			</div>
			<div class="textarea-filled textarea-neutral w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledNeutral"></textarea>
				<label class="textarea-filled-label" for="textareaFilledNeutral">Your bio</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="textarea-filled w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFilledDisabled" disabled
				></textarea>
				<label class="textarea-filled-label" for="textareaFilledDisabled">Your bio</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea is-valid" placeholder="Hello!!!" id="textareaFilledIsValid"
				></textarea>
				<label class="textarea-filled-label" for="textareaFilledIsValid">Your bio</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea is-invalid" placeholder="Hello!!!" id="textareaFilledIsInvalid"
				></textarea>
				<label class="textarea-filled-label" for="textareaFilledIsInvalid">Your bio</label>
			</div>
			<div class="textarea-floating w-full grow">
				<textarea class="textarea" placeholder="Hello!!!" id="textareaFloating"></textarea>
				<label class="textarea-floating-label" for="textareaFloating">Your bio</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-xs" placeholder="Hello!!!" id="filledTextareaXs"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareaXs">Your bio - xs</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-sm" placeholder="Hello!!!" id="filledTextareaSm"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareatSm">Your bio - sm</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-md" placeholder="Hello!!!" id="filledTextareaMd"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareaDefault">Your bio - default</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-lg" placeholder="Hello!!!" id="filledTextareaLg"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareaLg">Your bio - lg</label>
			</div>
			<div class="textarea-filled w-full grow">
				<textarea class="textarea textarea-xl" placeholder="Hello!!!" id="filledTextareaXl"
				></textarea>
				<label class="textarea-filled-label" for="filledTextareaXl">Your bio - xl</label>
			</div>
		</div>
		<div class="mb-5 flex grow flex-row gap-4">
			<div class="textarea-filled w-full grow">
				<textarea
					class="textarea textarea-xs sm:textarea-sm md:textarea-md lg:textarea-lg xl:textarea-xl"
					placeholder="Hello!!!"
					id="filledTextareaResponsive"
				></textarea>
				<label class="textarea-filled-label" for="filleTextareaResponsive">Your bio - responsive</label>
			</div>
			<div class="textarea-floating w-full grow">
				<textarea
					class="textarea textarea-xs sm:textarea-sm md:textarea-md lg:textarea-lg xl:textarea-xl"
					placeholder="Hello!!!"
					id="filledInputResponsive"
				></textarea>
				<label class="textarea-floating-label" for="filledTextareaResponsive"
					>Your bio - responsive</label
				>
			</div>
		</div>
		<!-- <div class="mb-5 flex grow flex-row flex-wrap gap-4">
			<div class="relative sm:w-56">
				<textarea
					placeholder="Primary colored input"
					class="textarea peer textarea-filled max-h-44 border-primary"
					id="primaryInput"
				></textarea>
				<label
					class="label-small md:label textarea-filled-label"
					style="color: oklch(var(--p));"
					for="primaryInput">Description</label
				>
				<span class="textarea-filled-focused" style="background-color: oklch(var(--p));"></span>
			</div>
			<div class="relative sm:w-56">
				<textarea
					placeholder="Secondary colored input"
					class="textarea peer textarea-filled max-h-44 border-secondary"
					id="secondaryTextarea"
				></textarea>
				<label
					class="label-small md:label textarea-filled-label"
					style="color: oklch(var(--s));"
					for="secondaryTextarea">Description</label
				>
				<span class="textarea-filled-focused" style="background-color: oklch(var(--s));"></span>
			</div>
			<div class="relative sm:w-56">
				<textarea
					placeholder="Accent colored input"
					class="textarea peer textarea-filled max-h-44 border-accent"
					id="accentTextarea"
				></textarea>
				<label
					class="label-small md:label textarea-filled-label"
					style="color: oklch(var(--a));"
					for="accentTextarea">Description</label
				>
				<span class="textarea-filled-focused" style="background-color: oklch(var(--a));"></span>
			</div>
			<div class="relative sm:w-56">
				<textarea
					placeholder="Neutral colored input"
					class="textarea peer textarea-filled max-h-44 border-neutral"
					id="neutraTextarea"
				></textarea>
				<label
					class="label-small md:label textarea-filled-label"
					style="color: oklch(var(--n));"
					for="secondaryTextarea">Description</label
				>
				<span class="textarea-filled-focused" style="background-color: oklch(var(--n));"></span>
			</div>
		</div> -->
	</div>

	<div>
		<Heading>Status sliders with Hue-Chroma-Tone</Heading>
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
					aria-label="left Status"
					id="leftStatus"
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
					aria-label="left Status"
					id="leftStatus"
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

	<div>
		<Heading>Icons</Heading>
		<p class="title-large text-center text-xl">Iconify with FlyonUI</p>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div>
				<p class="label text-center">
					Default library <span class="label-prominent badge min-h-fit">Tablers</span>
				</p>
				<span class="icon-[tabler--settings] size-12"></span>
				<span class="icon-[tabler--palette] size-12"></span>
				<span class="icon-[tabler--home] size-12"></span>
				<span class="icon-[tabler--user] size-12"></span>
				<span class="icon-[tabler--trash] size-12"></span>
				<span class="icon-[tabler--send-2] size-12"></span>
				<span class="icon-[tabler--share-2] size-12"></span>
				<span class="icon-[tabler--ban] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Material Symbols</span>
				</p>
				<span class="icon-[material-symbols--settings-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--palette-outline] size-12"></span>
				<span class="icon-[material-symbols--home-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--person-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--edit-outline-rounded] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">SVG spinners</span>
				</p>
				<span class="icon-[svg-spinners--12-dots-scale-rotate] size-12"></span>
				<span class="icon-[svg-spinners--3-dots-bounce] size-12"></span>
				<span class="icon-[svg-spinners--6-dots-rotate] size-12"></span>
				<span class="icon-[svg-spinners--90-ring-with-bg] size-12"></span>
				<span class="icon-[svg-spinners--clock] size-12"></span>
				<span class="icon-[svg-spinners--bars-scale] size-12"></span>
				<span class="icon-[svg-spinners--wifi] size-12"></span>
				<span class="icon-[svg-spinners--wifi-fade] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Font Awesome Solid</span>
				</p>
				<span class="icon-[fa6-solid--user] size-12"></span>
				<span class="icon-[fa6-solid--droplet] size-12"></span>
				<span class="icon-[fa6-solid--comments] size-12"></span>
				<span class="icon-[fa6-solid--plus] size-12"></span>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Font Awesome Brands</span>
				</p>
				<span class="icon-[fa6-brands--discord] size-12"></span>
				<span class="icon-[fa6-brands--youtube] size-12"></span>
				<span class="icon-[fa6-brands--linux] size-12"></span>
				<span class="icon-[fa6-brands--github] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Extension library <span class="label-prominent badge min-h-fit">Feather Icon</span>
				</p>
				<span class="icon-[fe--bell] size-12"></span>
				<span class="icon-[fe--disabled] size-12"></span>
				<span class="grid place-items-center">
					<span class="icon-[fe--bell] col-start-1 row-start-1 size-8"></span>
					<span class="icon-[fe--disabled] col-start-1 row-start-1 size-12"></span>
				</span>
			</div>
			<div>
				<p class="label text-center">
					Emoji library <span class="label-prominent badge min-h-fit">Noto emoji</span>
				</p>
				<span class="icon-[noto--folded-hands] size-12"></span>
				<span class="icon-[noto--folded-hands-medium-dark-skin-tone] size-12"></span>
				<span class="icon-[noto--heart-hands] size-12"></span>
				<span class="icon-[noto--heart-hands-dark-skin-tone] size-12"></span>
				<span class="icon-[noto--fire] size-12"></span>
				<span class="icon-[noto--smiling-face-with-sunglasses] size-12"></span>
				<span class="icon-[noto--check-mark-button] size-12"></span>
				<span class="icon-[noto--cross-mark] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Emoji library <span class="label-prominent badge min-h-fit">Openmoji</span>
				</p>
				<span class="icon-[openmoji--check-mark] size-12"></span>
				<span class="icon-[openmoji--cross-mark] size-12"></span>
			</div>
			<div>
				<p class="label text-center">
					Emoji library <span class="label-prominent badge min-h-fit">Twitter Emoji</span>
				</p>
				<span class="icon-[twemoji--flag-denmark] size-12"></span>
				<span class="icon-[twemoji--flag-germany] size-12"></span>
				<span class="icon-[twemoji--flag-united-states] size-12"></span>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<div>
		<Heading>Buttons</Heading>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div>
				<p class="label text-center">Action Buttons</p>
				<button class="btn-neutral-container btn btn-circle btn-gradient" aria-label="Add">
					<span class="icon-[fa6-solid--plus]"></span>
				</button>
				<button class="btn-info-container btn btn-circle btn-gradient" aria-label="Edit">
					<span class="icon-[material-symbols--edit-outline-rounded]"></span>
				</button>
				<button class="btn-error-container btn btn-circle btn-gradient" aria-label="Delete">
					<span class="icon-[tabler--trash]"></span>
				</button>
				<button class="btn-secondary-container btn btn-circle btn-gradient" aria-label="Send">
					<span class="icon-[tabler--send-2]"></span>
				</button>
				<button class="btn-success-container btn btn-circle btn-gradient" aria-label="Share">
					<span class="icon-[tabler--share-2]"></span>
				</button>
				<button class="btn-success-container btn btn-circle btn-gradient" aria-label="Done">
					<span class="icon-[mingcute--check-2-fill]"></span>
				</button>
				<p class="label text-center">State changing buttons</p>
				<button
					class="btn-info-container btn btn-circle btn-gradient"
					onclick={() => (edit ? (edit = false) : (edit = true))}
					aria-label="Edit Button"
				>
					<span class="grid place-items-center">
						<span class="icon-[material-symbols--edit-outline-rounded] col-start-1 row-start-1"
						></span>
						<span class="icon-[fe--disabled] col-start-1 row-start-1 size-6 {edit ? '' : 'hidden'}"
						></span>
					</span>
				</button>
			</div>
		</div>
	</div>

	<div>
		<Heading>Badges</Heading>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div>
				<p class="label text-center">Text Badges</p>
			</div>
		</div>
	</div>

	<div>
		<Heading>Tooltips</Heading>
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

	<div>
		<Heading>Theme Picker</Heading>
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

	<div>
		<Heading>Modal</Heading>
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

	<div>
		<Heading>Swaps</Heading>
		<div class="grid grid-cols-12 gap-4">
			<div>
				<label class="swap">
					<input type="checkbox" />
					<span class="icon-[tabler--volume] swap-on size-6"></span>
					<span class="icon-[tabler--volume-off] swap-off size-6"></span>
				</label>
			</div>
			<div>
				<label class="btn btn-circle swap swap-rotate">
					<input type="checkbox" />
					<span class="icon-[tabler--menu-2] swap-off"></span>
					<span class="icon-[tabler--x] swap-on"></span>
				</label>
			</div>
			<div>
				<label class="swap swap-rotate">
					<input type="checkbox" />
					<span class="icon-[tabler--sun] swap-on size-6"></span>
					<span class="icon-[tabler--moon] swap-off size-6"></span>
				</label>
			</div>
			<div>
				<label class="swap swap-flip text-6xl">
					<input type="checkbox" />
					<span class="swap-on">😈</span>
					<span class="swap-off">😇</span>
				</label>
			</div>
			<!-- <div>
					<label bind:this={myTemperature} class="swap swap-js text-6xl">
						<span class="swap-on">🥵</span>
						<span class="swap-off">🥶</span>
					</label>
					<label class="swap swap-js text-6xl">
						<span class="swap-on">🥳</span>
						<span class="swap-off">😭</span>
					</label>
				</div> -->
			<div>
				<label class="btn btn-circle swap swap-rotate">
					<input type="checkbox" />
					<span class="icon-[tabler--player-play] swap-off"></span>
					<span class="icon-[tabler--player-pause] swap-on"></span>
				</label>
			</div>
		</div>

		<HorizontalRule />
	</div>

	<!-- This local override works:
		style="background-color: var(--my-color); color: var(--md-sys-color-on-primary);" -->
	<div>
		<Heading>Drawer (Sidebar)</Heading>
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
