<script lang="ts">
	import { themeStore } from '$lib/stores';
	import type { AppTheme } from '$lib/theming';
	import { Hct, hexFromArgb } from '@material/material-color-utilities';
	import { onDestroy } from 'svelte';
	import Heading from '$components/Heading.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import type { IOverlay } from 'flyonui/flyonui';

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

	// for modal and drawer:
	const loadHSOverlay = async () => {
		const { HSOverlay } = await import('flyonui/flyonui.js');
		return HSOverlay;
	};

	let myModal: HTMLElement;
	let overlay: IOverlay | undefined = $state();

	$effect(() => {
		loadHSOverlay().then((loadHSOverlay) => {
			overlay = new loadHSOverlay(myModal);
		});
	});

	const openModal = () => {
		overlay?.open();
	};
</script>

<div class="w-full xl:grid xl:grid-cols-2 xl:gap-4">
	<div>
		<Heading>Card with chat</Heading>
		<div class="mb-5 grid justify-items-center">
			<div
				class="card w-full rounded-xl border-[1px] border-outline-variant bg-base-250 shadow-lg shadow-outline-variant md:w-4/5"
			>
				<div class="card-header">
					<h5 class="text-title md:text-title-large card-title">Chat card</h5>
				</div>
				<div class="card-body">
					<div
						class="max-h-96 min-h-44 overflow-y-auto rounded-lg bg-base-200 p-2 shadow-inner shadow-outline"
					>
						<div class="chat chat-receiver">
							<div class="avatar chat-avatar">
								<div class="size-10 rounded-full">
									<span class="icon-[tabler--man] m-1 size-8 text-primary"></span>
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
									<span class="icon-[tabler--user] m-1 size-8 text-primary"></span>
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
				</div>
				<div class="card-footer flex flex-row items-center gap-2">
					<div class="relative grow">
						<input
							type="text"
							placeholder="Send a message here"
							class="input input-filled peer grow border-secondary shadow-sm shadow-outline"
							id="chattMessage"
						/>
						<label
							class="text-label-small md:text-label input-filled-label grow"
							style="color: oklch(var(--s));"
							for="chatMessage">♡ What's on your heart?</label
						>
						<span class="input-filled-focused grow" style="background-color: oklch(var(--s));"
						></span>
					</div>
					<button
						class="btn-secondary-container btn btn-circle btn-gradient"
						aria-label="Add Icon Button"><span class="icon-[tabler--send-2]"></span></button
					>
				</div>
			</div>
		</div>
	</div>

	<div>
		<Heading>Card with text and navigation</Heading>
		<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
			<div
				class="card rounded-xl border-[1px] border-outline-variant bg-base-250 shadow-lg shadow-outline-variant"
			>
				<div class="card-header">
					<h5 class="text-title-small md:text-title lg:text-title-large base-content card-title">
						Here's a title
					</h5>
				</div>
				<div class="card-body">
					<p class="text-body-small md:text-body text-primary-container-content">
						Some test text, here. Can go over several lines. And if it does, the cards in the same
						line will adjust to the longest card. This is a good way to keep the layout clean and
						consistent.
					</p>
				</div>
				<div class="card-footer">
					<div class="card-actions text-center">
						<a href="#top"
							><button
								class="text-label-small btn btn-primary rounded-full px-3 text-primary-content shadow-primary"
								>Link to top of page</button
							></a
						>
					</div>
				</div>
			</div>
			<div
				class="card rounded-xl border-[1px] border-outline-variant bg-base-250 shadow-lg shadow-outline-variant"
			>
				<div class="card-header">
					<h5 class="text-title-small md:text-title lg:text-title-large base-content card-title">
						One more title
					</h5>
				</div>
				<div class="card-body">
					<p class="text-body-small md:text-body text-primary-container-content">
						Some shorter text here - but adjusts to the height of the neigour card
					</p>
				</div>
				<div class="card-footer">
					<div class="card-actions text-center">
						<a href="#top"
							><button
								class="text-label-small btn btn-primary rounded-full px-3 text-primary-content shadow-primary"
								>Link to top of page</button
							></a
						>
					</div>
				</div>
			</div>
			<div
				class="card rounded-xl border-[1px] border-outline-variant bg-base-250 shadow-lg shadow-outline-variant"
			>
				<div class="card-header">
					<h5 class="text-title-small md:text-title lg:text-title-large base-content card-title">
						A third title
					</h5>
				</div>
				<div class="card-body">
					<p class="text-body-small md:text-body text-primary-container-content">
						This one is meant to fill the row. Note how the cards are responsive on smaller screens.
					</p>
				</div>
				<div class="card-footer">
					<div class="card-actions text-center">
						<a href="#top"
							><button
								class="text-label-small btn btn-primary rounded-full px-3 text-primary-content shadow-primary"
								>Link to top of page</button
							></a
						>
					</div>
				</div>
			</div>
		</div>
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
		<p class="text-title-large text-center text-xl">Iconify with FlyonUI</p>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div>
				<p class="text-label text-center">
					Default library <span class="text-label-prominent badge min-h-fit">Tablers</span>
				</p>
				<span class="icon-[tabler--settings] size-12"></span>
				<span class="icon-[tabler--palette] size-12"></span>
				<span class="icon-[tabler--home] size-12"></span>
				<span class="icon-[tabler--user] size-12"></span>
				<span class="icon-[tabler--trash] size-12"></span>
				<span class="icon-[tabler--send-2] size-12"></span>
				<span class="icon-[tabler--share-2] size-12"></span>
			</div>
			<div>
				<p class="text-label text-center">
					Extension library <span class="text-label-prominent badge min-h-fit"
						>Material Symbols</span
					>
				</p>
				<span class="icon-[material-symbols--settings-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--palette-outline] size-12"></span>
				<span class="icon-[material-symbols--home-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--person-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--edit-outline-rounded] size-12"></span>
			</div>
			<div>
				<p class="text-label text-center">
					Extension library <span class="text-label-prominent badge min-h-fit">SVG spinners</span>
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
				<p class="text-label text-center">
					Extension library <span class="text-label-prominent badge min-h-fit"
						>Font Awesome Solid</span
					>
				</p>
				<span class="icon-[fa6-solid--droplet] size-12"></span>
				<span class="icon-[fa6-solid--comments] size-12"></span>
				<span class="icon-[fa6-solid--plus] size-12"></span>
				<p class="text-label text-center">
					Extension library <span class="text-label-prominent badge min-h-fit"
						>Font Awesome Brands</span
					>
				</p>
				<span class="icon-[fa6-brands--discord] size-12"></span>
				<span class="icon-[fa6-brands--youtube] size-12"></span>
				<span class="icon-[fa6-brands--linux] size-12"></span>
				<span class="icon-[fa6-brands--github] size-12"></span>
			</div>
			<div>
				<p class="text-label text-center">
					Emoji library <span class="text-label-prominent badge min-h-fit">Noto emoji</span>
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
				<p class="text-label text-center">
					Emoji library <span class="text-label-prominent badge min-h-fit">Openmoji</span>
				</p>
				<span class="icon-[openmoji--check-mark] size-12"></span>
				<span class="icon-[openmoji--cross-mark] size-12"></span>
			</div>
			<div>
				<p class="text-label text-center">
					Emoji library <span class="text-label-prominent badge min-h-fit">Twitter Emoji</span>
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
				<p class="text-label text-center">Action Buttons</p>
				<button class="btn-neutral-container btn btn-circle btn-gradient" aria-label="Add Button">
					<span class="icon-[fa6-solid--plus]"></span>
				</button>
				<button class="btn-info-container btn btn-circle btn-gradient" aria-label="Edit Button">
					<span class="icon-[material-symbols--edit-outline-rounded]"></span>
				</button>
				<button class="btn-error-container btn btn-circle btn-gradient" aria-label="Delete Button">
					<span class="icon-[tabler--trash]"></span>
				</button>
				<button
					class="btn-secondary-container btn btn-circle btn-gradient"
					aria-label="Send Button"
				>
					<span class="icon-[tabler--send-2]"></span>
				</button>
				<button
					class="btn-success-container btn btn-circle btn-gradient"
					aria-label="Share Button"
				>
					<span class="icon-[tabler--share-2]"></span>
				</button>
			</div>
		</div>
	</div>

	<div>
		<Heading>Badges</Heading>
		<div class="grid grid-cols-3 gap-4 sm:grid-cols-5">
			<div>
				<p class="text-label text-center">Text Badges</p>
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
					{#each allContrasts as _}
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
			onclick={openModal}
		>
			Open modal
		</button>

		<!-- <div bind:this={modal} id="basic-modal" class="overlay modal overlay-open:opacity-100 hidden" role="dialog" tabindex="-1"> -->
		<div
			bind:this={myModal}
			id="basic-modal"
			class="overlay modal hidden overlay-open:opacity-100"
			role="dialog"
			tabindex="-1"
		>
			<div class="modal-dialog overlay-open:opacity-100">
				<div class="modal-content bg-base-300">
					<div class="modal-header">
						<h3 class="modal-text-title">Dialog Title</h3>
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
			class="overlay drawer drawer-start hidden overlay-open:translate-x-0"
			role="dialog"
			tabindex="-1"
		>
			<div class="drawer-header">
				<h3 class="drawer-text-title">Drawer Title</h3>
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
