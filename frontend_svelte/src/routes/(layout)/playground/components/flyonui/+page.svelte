<script lang="ts">
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	// import { createRawSnippet, type Snippet } from 'svelte';
	import type { IOverlay } from 'flyonui/flyonui';

	// const createdComponent: Snippet = createRawSnippet(() => {
	// return {
	// 	render: () => ``
	// 	// setup: (element: Element) => {}
	// };
	// });

	// let isDrawerOpen = $state(false);

	// const toggleDrawer = () => {
	// 	isDrawerOpen = !isDrawerOpen;
	// 	console.log('Drawer toggled to ' + isDrawerOpen);
	// }
	// const closeDrawer = () => isDrawerOpen = false;

    let sourceColor = $state('#769CDF');
    let variant = $state('TONAL_SPOT');
    const contrastMin = -1.0
    const contrastMax = 1.0
    const contrastStep = 0.1
    const allContrasts = Array.from({ length: (contrastMax - contrastMin) / contrastStep + 1 }, (_, i) => contrastMin + i * contrastStep);
    let contrast = $state(0.0);
    // $effect(() => console.log('sourceColor:', sourceColor, 'variant:', variant));

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

<div class="mx-5 grid grid-cols-1 gap-4 xl:grid-cols-2">
	<div class="col-span-2">
		<Title>Colors</Title>
        <p class="text-center text-2xl">Semantic colors FlyonUI:</p>
		<div class="grid grid-cols-4 xl:grid-cols-8 gap-4">
            <div>
                <div class="skeleton flex h-24 w-36 items-center justify-center bg-primary">
                    <p class="text-center text-xl text-primary-content">primary</p>
                    <!-- <p class="text-center text-xl">primary</p> -->
                </div>
                <div class="skeleton flex h-24 w-36 items-center justify-center bg-primary-content">
                    <p class="text-center text-xl text-primary">primary content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-secondary">
                    <p class="text-center text-xl text-secondary-content">secondary</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-secondary-content">
                    <p class="text-center text-xl text-secondary">secondary-content</p>
                </div>
            </div>
            <!-- <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-tertiary">
                    <p class="text-center text-xl text-tertiary-content">tertiary</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-tertiary-content">
                    <p class="text-center text-xl text-tertiary">tertiary-content</p>
                </div>
            </div> -->
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-accent">
                    <p class="text-center text-xl text-accent-content">accent</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-accent-content">
                    <p class="text-center text-xl text-accent">accent-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-neutral">
                    <p class="text-center text-xl text-neutral-content">neutral</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-neutral-content">
                    <p class="text-center text-xl text-neutral">neutral-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-info">
                    <p class="text-center text-xl text-info-content">info</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-info-content">
                    <p class="text-center text-xl text-info">info-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-success">
                    <p class="text-center text-xl text-success-content">success</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-success-content">
                    <p class="text-center text-xl text-success">success-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-warning">
                    <p class="text-center text-xl text-warning-content">warning</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-warning-content">
                    <p class="text-center text-xl text-warning">waring-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-error">
                    <p class="text-center text-xl text-error-content">error</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-error-content">
                    <p class="text-center text-xl text-error">error-content</p>
                </div>
            </div>
        </div>
        <p class="text-center text-2xl">Added to FlyonUI to match Material UI:</p>
		<div class="grid grid-cols-4 xl:grid-cols-8 gap-4">
            <div>
                <div class="skeleton flex h-24 w-36 items-center justify-center bg-primary-container">
                    <p class="text-center text-xl text-primary-content-container">primary container</p>
                </div>
                <div class="skeleton flex h-24 w-36 items-center justify-center bg-primary-content-container">
                    <p class="text-center text-xl text-primary-container">primary content container</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-secondary">
                    <p class="text-center text-xl text-secondary-content">secondary</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-secondary-content">
                    <p class="text-center text-xl text-secondary">secondary-content</p>
                </div>
            </div>
            <!-- <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-tertiary">
                    <p class="text-center text-xl text-tertiary-content">tertiary</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-tertiary-content">
                    <p class="text-center text-xl text-tertiary">tertiary-content</p>
                </div>
            </div> -->
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-accent">
                    <p class="text-center text-xl text-accent-content">accent</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-accent-content">
                    <p class="text-center text-xl text-accent">accent-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-neutral">
                    <p class="text-center text-xl text-neutral-content">neutral</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-neutral-content">
                    <p class="text-center text-xl text-neutral">neutral-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-info">
                    <p class="text-center text-xl text-info-content">info</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-info-content">
                    <p class="text-center text-xl text-info">info-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-success">
                    <p class="text-center text-xl text-success-content">success</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-success-content">
                    <p class="text-center text-xl text-success">success-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-warning">
                    <p class="text-center text-xl text-warning-content">warning</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-warning-content">
                    <p class="text-center text-xl text-warning">waring-content</p>
                </div>
            </div>
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-error">
                    <p class="text-center text-xl text-error-content">error</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-error-content">
                    <p class="text-center text-xl text-error">error-content</p>
                </div>
            </div>
        </div>
        <p class="text-center text-2xl">Background colors FlyonUI:</p>
        <div class="grid grid-cols-5 gap-4">
            <div class="skeleton flex h-12 w-36 items-center justify-center bg-base-100">
                <p class="text-center text-xl">base-100</p>
            </div>
            <div class="skeleton flex h-12 w-36 items-center justify-center bg-base-200">
                <p class="text-center text-xl">base-200</p>
            </div>
            <div class="skeleton flex h-12 w-36 items-center justify-center bg-base-300">
                <p class="text-center text-xl">base-300</p>
            </div>
			<div class="skeleton flex h-12 w-36 items-center justify-center bg-base-content">
				<p class="text-center text-xl text-secondary-content">base-content</p>
			</div>
			<div class="skeleton flex h-12 w-36 items-center justify-center bg-base-shadow">
				<p class="text-center text-xl text-secondary-content">base-shadow</p>
			</div>
        </div>
        <p class="text-center text-2xl">Background base colors with /x argument:</p>
        <div class="grid grid-cols-11 gap-4">
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content">
				<p class="text-center text-xl"></p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/10">
				<p class="text-center text-xl">/10</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/20">
				<p class="text-center text-xl">/20</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/30">
				<p class="text-center text-xl">/30</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/40">
				<p class="text-center text-xl">/40</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/50">
				<p class="text-center text-xl">/50</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/60">
				<p class="text-center text-xl">/60</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/70">
				<p class="text-center text-xl">/70</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/80">
				<p class="text-center text-xl">/80</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/90">
				<p class="text-center text-xl">/90</p>
			</div>
			<div class="skeleton flex h-12 w-12 items-center justify-center bg-primary-content/100">
				<p class="text-center text-xl">/100</p>
			</div>
		</div>
	</div>

	<div>
		<Title>Fonts</Title>
		<link rel="preconnect" href="https://fonts.googleapis.com" />
		<p class="font-sans">
			Some text in <em>sans</em> font family, should be using <b>Robot</b> Google Fonts extending default theme in <code>tailwindcss.config.js</code>.
		</p>
		<p class="font-serif">
			Some text in <em>serif</em> font family, should be using <b>Merriweather</b> Google Fonts, extending default theme in <code>tailwindcss.config.js</code>.
		</p>
		<p class="font-mono">
			Some text in <em>mono</em> font family, still <b>TailwindCSS</b> default, not overwritten in
			<code>tailwindcss.config.js</code> yet
		</p>
	</div>

    <div>
        <Title>Styles</Title>
        Targets with their default values:
        <ul>
            <li>--rounded-box: 0.5rem ;</li>
            <li>--rounded-btn: 0.375rem;</li>
            <li>--rounded-tooltip: 0.25rem;</li>
            <li>--animation-btn: 0.25s;</li>
            <li>--animation-input: .2s;</li>
            <li>--btn-focus-scale: 0.95;</li>
            <li>--border-btn: 1px;</li>
            <li>--tab-border: 1px;</li>
            <li>--tab-radius: 0.5rem;</li>
        </ul>
    </div>

    <div>
        <Title>Icons</Title>
        <p>Integrated with FlyonUI: </p>
    </div>

    <div>
        <Title>Theme Picker</Title>
        <div class="grid grid-cols-3 gap-4">
            <div class="w-48">
                <label class="label label-text" for="colorPicker">Source color
                    <span class="label">
                        <code class="label-text-alt">{sourceColor}</code>
                    </span>
                </label>
                <input class="input" type="color" id="colorPicker" name="color-picker" bind:value={sourceColor} />
                
            </div>
            <div class="relative w-48">
                <label class="label label-text" for="themeVariant">Variant</label>
                <select class="select select-floating max-w-sm" aria-label="Select variant" id="themeVariant" bind:value={variant}>
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
                <label class="label label-text" for="contrast">Contrast: <span class="label">
                    <code class="label-text-alt">{contrast}</code>
                </span></label>
                
                <input type="range" min={contrastMin} max={contrastMax} step={contrastStep} class="range w-full"  aria-label="contrast" id="contrast" bind:value={contrast}/>
                <div class="w-full flex justify-between text-xs px-2">
                    
                    {#each allContrasts as _}
                        <span>|</span>
                    {/each}
                </div>
                
            </div>
        </div>
    </div>

	<div>
		<Title>Modal</Title>
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
				<div class="modal-content">
					<div class="modal-header">
						<h3 class="modal-title">Dialog Title</h3>
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
		<Title>Swaps</Title>
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
		<Title>Drawer (Sidebar)</Title>
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

	<div>
		<Title>Card</Title>
		<div class="card sm:max-w-sm">
			<div class="card-body">
				<h5 class="card-title mb-2.5">Body of a Card here</h5>
				<p class="mb-4">
					Soe text to fill in the body fo the card. This could be anything here. But for now just
					text filling in here.
				</p>
				<div class="card-actions">
					<button class="btn btn-primary">Card button</button>
				</div>
			</div>
		</div>
	</div>

	<!-- <div>
        <Title>Menus</Title>
        <div class="grid grid-cols-6 gap-4">
            <div>
                <ul class="menu w-64 space-y-0.5 [&_.nested-collapse-wrapper]:space-y-0.5 [&_ul]:space-y-0.5">
                    <li>
                    <a href="#">
                        <span class="icon-[tabler--home] size-5"></span>
                        Home
                    </a>
                    </li>
                    <li class="space-y-0.5">
                    <a class="collapse-toggle collapse-open:bg-primary-content/10 open" id="menu-app" data-collapse="#menu-app-collapse">
                        <span class="icon-[tabler--apps] size-5"></span>
                        Apps
                        <span class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"></span>
                    </a>
                    <ul id="menu-app-collapse" class="open collapse w-auto overflow-hidden transition-[height] duration-300" aria-labelledby="menu-app">
                        <li>
                        <a href="#">
                            <span class="icon-[tabler--message] size-5"></span>
                            Chat
                        </a>
                        </li>
                        <li>
                        <a href="#">
                            <span class="icon-[tabler--calendar] size-5"></span>
                            Calendar
                        </a>
                        </li>
                        <li class="nested-collapse-wrapper">
                        <a class="collapse-toggle nested-collapse open" id="sub-menu-academy" data-collapse="#sub-menu-academy-collapse">
                            <span class="icon-[tabler--book] size-5"></span>
                            Academy
                            <span class="icon-[tabler--chevron-down] collapse-icon size-4"></span>
                        </a>
                        <ul id="sub-menu-academy-collapse" class="open collapse w-auto overflow-hidden transition-[height] duration-300" aria-labelledby="sub-menu-academy">
                            <li>
                            <a href="#">
                                <span class="icon-[tabler--books] size-5"></span>
                                Courses
                            </a>
                            </li>
                            <li>
                            <a href="#">
                                <span class="icon-[tabler--list-details] size-5"></span>
                                Course details
                            </a>
                            </li>
                            <li class="nested-collapse-wrapper">
                            <a class="collapse-toggle nested-collapse open" id="sub-menu-academy-stats" data-collapse="#sub-menu-academy-stats-collapse">
                                <span class="icon-[tabler--chart-bar] size-5"></span>
                                Stats
                                <span class="icon-[tabler--chevron-down] collapse-icon size-4"></span>
                            </a>
                            <ul id="sub-menu-academy-stats-collapse" class="open collapse w-auto overflow-hidden transition-[height] duration-300" aria-labelledby="sub-menu-academy-stats">
                                <li>
                                <a href="#">
                                    <span class="icon-[tabler--chart-donut] size-5"></span>
                                    Goals
                                </a>
                                </li>
                            </ul>
                            </li>
                        </ul>
                        </li>
                    </ul>
                    </li>
                    <li>
                    <a href="#">
                        <span class="icon-[tabler--settings] size-5"></span>
                        Settings
                    </a>
                    </li>
                </ul>
            </div>
        </div>
    </div> -->
</div>

<style>
/* body, html {
    --p: var(--md-sys-color-primary);
    --pc: var(--md-sys-color-on-primary);
} */

/* Applying material design colors to new classes works: */
/* .primary {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
} */

/* Consider merging text and background into one: */
/* color: var(--md-sys-color-on-primary); */

/* Consider merging text and background into one: */
/* background-color: var(--md-sys-color-on-primary); */

/* .bg-primary, .btn-primary {
    background-color: var(--md-sys-color-primary);
    
}
.text-primary {
    
    color: var(--md-sys-color-primary);
}
.bg-primary-content, .btn-primary-content {
    background-color: var(--md-sys-color-on-primary);
}
.text-primary-content {
    color: var(--md-sys-color-on-primary);
}

.bg-primary-container, .btn-primary-container {
    background-color: var(--md-sys-color-primary-container);
}
.text-primary-container {
    color: var(--md-sys-color-primary-container);
}
.bg-primary-content-container, .btn-primary-content-container {
    background-color: var(--md-sys-color-on-primary-container);
}
.text-primary-content-container {
    color: var(--md-sys-color-on-primary-container);
} */
</style>