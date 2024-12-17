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

<div class="grid grid-cols-1 xl:grid-cols-2  gap-4 mx-5">

    <div>
        <Title>Colors</Title>
        <div class="grid grid-cols-12 gap-4">
            <p class="col-span-12">Semantic colors FlyonUI:</p>
            <div class="skeleton bg-primary w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">1</p></div>
            <div class="skeleton bg-primary-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">2</p></div>
            <div class="skeleton bg-secondary w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">3</p></div>
            <div class="skeleton bg-secondary-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">4</p></div>
            <div class="skeleton bg-accent w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">5</p></div>
            <div class="skeleton bg-accent-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">6</p></div>
            <div class="skeleton bg-neutral w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">7</p></div>
            <div class="skeleton bg-neutral-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">8</p></div>
            <div class="skeleton bg-base-100 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">9</p></div>
            <div class="skeleton bg-base-200 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">10</p></div>
            <div class="skeleton bg-base-300 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">11</p></div>
            <div class="skeleton bg-base-400 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">12</p></div>
            <div class="skeleton bg-base-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">13</p></div>
            <div class="skeleton bg-base-shadow w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">14</p></div>
            <div class="skeleton bg-info w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">15</p></div>
            <div class="skeleton bg-info-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">16</p></div>
            <div class="skeleton bg-success w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">17</p></div>
            <div class="skeleton bg-success-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">18</p></div>
            <div class="skeleton bg-warning w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">19</p></div>
            <div class="skeleton bg-warning-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">20</p></div>
            <div class="skeleton bg-error w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">21</p></div>
            <div class="skeleton bg-error-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">22</p></div>
            <p class="col-span-12">Background base content colors with /x argument:</p>
            <div class="skeleton bg-base-content w-12 h-12 flex items-center justify-center"><p class="text-center text-xl"></p></div>
            <div class="skeleton bg-base-content/10 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/10</p></div>
            <div class="skeleton bg-base-content/20 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/20</p></div>
            <div class="skeleton bg-base-content/30 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/30</p></div>
            <div class="skeleton bg-base-content/40 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/40</p></div>
            <div class="skeleton bg-base-content/50 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/50</p></div>
            <div class="skeleton bg-base-content/60 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/60</p></div>
            <div class="skeleton bg-base-content/70 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/70</p></div>
            <div class="skeleton bg-base-content/80 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/80</p></div>
            <div class="skeleton bg-base-content/90 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/90</p></div>
            <div class="skeleton bg-base-content/100 w-12 h-12 flex items-center justify-center"><p class="text-center text-xl">/100</p></div>
        </div>
    </div>


    <div>
        <Title>Fonts</Title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <p class="font-sans">Some text in <em>sans</em> font family, should be using <b>Robot</b> Google Fonts</p>
        <p class="font-serif">Some  text in <em>serif</em> font family, should be using <b>Merriweather</b> Google Fonts</p>
        <p class="font-mono">Some text in <em>mono</em> font family, still <b>TailwindCSS</b> default, not overwritten in <code>tailwindcss.config.js</code> yet</p>
    </div>

    <div>
        <Title>Modal</Title>
        <button
            type="button"
            class="btn btn-primary"
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
                    Soe text to fill in the body fo the card. This could be anything here. But for now just text
                    filling in here.
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
                    <a class="collapse-toggle collapse-open:bg-base-content/10 open" id="menu-app" data-collapse="#menu-app-collapse">
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
