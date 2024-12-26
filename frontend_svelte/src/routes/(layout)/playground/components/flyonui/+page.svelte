<script lang="ts">
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	// import { createRawSnippet, type Snippet } from 'svelte';
	import type { IOverlay } from 'flyonui/flyonui';
	import ColorTileFlyonUi from '$components/ColorTileFlyonUI.svelte';
    import { Theming } from '$lib/theming';

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
	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
	const allContrasts = Array.from(
		{ length: (contrastMax - contrastMin) / contrastStep + 1 },
		(_, i) => contrastMin + i * contrastStep
	);
	let contrast = $state(0.0);
	// $effect(() => console.log('sourceColor:', sourceColor, 'variant:', variant, 'contrast:', contrast));

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

    // This is getting the resolved CSS after FlyonUI, Tailwind CSS and so on processing - don't alter that."
    $effect(() => Theming.addBackgroundUtilityClass('primary-container', ['var(--md-sys-color-primary-container)']));
	$effect(() => Theming.addBackgroundUtilityClass('inverse-primary', ['var(--md-sys-color-inverse-primary)']));
	$effect(() => Theming.addFillUtilityClass('inverse-primary', ['var(--md-sys-color-inverse-primary)']));
</script>

<!-- // based on https://github.com/themeselection/flyonui/blob/bdbdaeec6b575b80283f5fda51abd3981a168fca/src/theming/index.js#L2
// match with Material Designs color palette
// export const flyonUIColorObject = {
//     transparent: 'transparent',
//     current: 'currentColor',

//     primary: '#794DFF',
//     'primary-content': '#794DFF',

//     secondary: 'var(--fallback-s,oklch(var(--s)/<alpha-value>))',
//     'secondary-content': 'var(--fallback-sc,oklch(var(--sc)/<alpha-value>))',

//     accent: 'var(--fallback-a,oklch(var(--a)/<alpha-value>))',
//     'accent-content': 'var(--fallback-ac,oklch(var(--ac)/<alpha-value>))',

//     neutral: 'var(--fallback-n,oklch(var(--n)/<alpha-value>))',
//     'neutral-content': 'var(--fallback-nc,oklch(var(--nc)/<alpha-value>))',

//     'base-100': 'var(--fallback-b1,oklch(var(--b1)/<alpha-value>))',
//     'base-200': 'var(--fallback-b2,oklch(var(--b2)/<alpha-value>))',
//     'base-300': 'var(--fallback-b3,oklch(var(--b3)/<alpha-value>))',
//     'base-content': 'var(--fallback-bc,oklch(var(--bc)/<alpha-value>))',

//     'base-shadow': 'var(--fallback-bs,oklch(var(--bs)/<alpha-value>))',

//     info: 'var(--fallback-in,oklch(var(--in)/<alpha-value>))',
//     'info-content': 'var(--fallback-inc,oklch(var(--inc)/<alpha-value>))',

//     success: 'var(--fallback-su,oklch(var(--su)/<alpha-value>))',
//     'success-content': 'var(--fallback-suc,oklch(var(--suc)/<alpha-value>))',

//     warning: 'var(--fallback-wa,oklch(var(--wa)/<alpha-value>))',
//     'warning-content': 'var(--fallback-wac,oklch(var(--wac)/<alpha-value>))',
//     error: 'var(--fallback-er,oklch(var(--er)/<alpha-value>))',

//     'error-content': 'var(--fallback-erc,oklch(var(--erc)/<alpha-value>))'
// } -->

<div class="w-full xl:grid xl:gap-4 xl:grid-cols-2">
	<div class="col-span-2">
		<Title>Colors</Title>
        <div class="accordion accordion-bordered divide-y" data-accordion-always-open="">
            <!-- <div class="accordion-item accordion-item-active:scale-[1.05] accordion-item-active:mb-3 ease-in duration-300 delay-[1ms] active" id="default-colors"> -->
            <div class="accordion-item active" id="default-colors">
                <button class="accordion-toggle inline-flex items-center gap-x-4 text-start" aria-controls="default-foreground-colors-collapse" aria-expanded="true">
                    <span class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180" ></span>
                    <p class="ml-10 text-xl">
                        Default foreground colors FlyonUI
                    </p>
                </button>
                <div id="default-foreground-colors-collapse" class="accordion-content w-full overflow-hidden transition-[height] duration-300" aria-labelledby="default-foreground-colors" role="region">
                    <div class="m-5 grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-8">
                        <div>
                            <ColorTileFlyonUi background="primary" content="primary-content" />
                            <ColorTileFlyonUi background="primary-content" content="primary" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="secondary" content="secondary-content" />
                            <!-- Programmatically applied classes don't show up, unless they are references elsewhere in the DOM due to Svelte's tree-shaking -->
                            <ColorTileFlyonUi background="secondary-content" content="secondary" />
                            <!-- <hr /> -->
                            <!-- <div class="flex h-24 grow bg-secondary-content p-2">
                                <p class="text-left text-base text-secondary md:text-xl">secondary content direct</p>
                            </div>
                            <hr /> -->
                            <!-- <ColorTileFlyonUi background="onSecondary" content="secondary" /> -->
                        </div>
                        <div>
                            <ColorTileFlyonUi background="accent" content="accent-content" />
							<div class="bg-accent">TEST</div>
                            <ColorTileFlyonUi background="accent-content" content="accent" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="neutral" content="neutral-content" />
                            <ColorTileFlyonUi background="neutral-content" content="neutral" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="info" content="info-content" />
                            <ColorTileFlyonUi background="info-content" content="info" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="success" content="success-content" />
                            <ColorTileFlyonUi background="success-content" content="success" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="warning" content="warning-content" />
                            <ColorTileFlyonUi background="warning-content" content="warning" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="error" content="error-content" />
                            <ColorTileFlyonUi background="error-content" content="error" />
                        </div>
                    </div>
                </div>
            </div>
            <div class="accordion-item active" id="default-background-colors">
                <button class="accordion-toggle inline-flex items-center gap-x-4 text-start" aria-controls="default-background-colors-collapse" aria-expanded="true">
                    <span class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180" ></span>
                    <p class="ml-10 text-xl">Default background colors FlyonU</p>
                </button>
                <div id="default-background-colors-collapse" class="accordion-content w-full overflow-hidden transition-[height] duration-300" aria-labelledby="default-background-colors" role="region">
                    <div class="m-5 grid grid-cols-2 md:grid-cols-5 gap-4">
                        <ColorTileFlyonUi background="base-100" />
                        <ColorTileFlyonUi background="base-200" />
                        <ColorTileFlyonUi background="base-300" />
                        <ColorTileFlyonUi background="base-content" content="onSecondary" />
                        <ColorTileFlyonUi background="base-shadow" />
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
                            <p class="text-center text-xl text-base-content">base-shadow</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="accordion-item active" id="opacity-colors">
                <button class="accordion-toggle inline-flex items-center gap-x-4 text-start" aria-controls="opacity-colors-collapse" aria-expanded="true">
                    <span class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180" ></span>
                    <p class="ml-10 text-xl">Applying tailwind /x argument for opacity</p>
                </button>
                <div id="opacity-colors-collapse" class="accordion-content w-full overflow-hidden transition-[height] duration-300" aria-labelledby="opacity-colors" role="region">
					<p class="ml-5">Primary:</p>
                    <div class="m-5 grid grid-cols-11 gap-4">
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary">
                            <p class="text-center text-xl"></p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/10">
                            <p class="text-center text-xl">/10</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/20">
                            <p class="text-center text-xl">/20</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/30">
                            <p class="text-center text-xl">/30</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/40">
                            <p class="text-center text-xl">/40</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/50">
                            <p class="text-center text-xl">/50</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/60">
                            <p class="text-center text-xl">/60</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/70">
                            <p class="text-center text-xl">/70</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/80">
                            <p class="text-center text-xl">/80</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/90">
                            <p class="text-center text-xl">/90</p>
                        </div>
                        <div class="skeleton flex h-12 w-12 items-center justify-center bg-primary/100">
                            <p class="text-center text-xl">/100</p>
                        </div>
                    </div>
					<br />
					<p class="ml-5">Primary content:</p>
                    <div class="m-5 grid grid-cols-11 gap-4">
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
            </div>
            <div class="accordion-item active" id="extension-materialui-colors">
                <button class="accordion-toggle inline-flex items-center gap-x-4 text-start" aria-controls="extension-materialui-colors-collapse" aria-expanded="true">
                    <span class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180" ></span>
                    <p class="ml-10 text-xl">Extensions for foreground to FlyonUI with extra Material UI colors</p>
                </button>
                <div id="extension-materialui-colors-collapse" class="accordion-content w-full overflow-hidden transition-[height] duration-300" aria-labelledby="extension-materialui-colors" role="region">
                    <div class="m-5 grid grid-cols-4 gap-4 xl:grid-cols-8">
                        <div>
                            <ColorTileFlyonUi background="primary-container" content="primary-container-content" />
                            <ColorTileFlyonUi background="primary-container-content" content="primary-container" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="secondary-container" content="secondary-container-content" />
                            <ColorTileFlyonUi background="secondary-container-content" content="secondary-container" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="accent-container" content="accent-container-content" />
                            <ColorTileFlyonUi background="accent-container-content" content="accent-container" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="neutral-container" content="neutral-container-content" />
                            <ColorTileFlyonUi background="neutral-container-content" content="neutral-container" />
                        </div>
						<div>
                            <ColorTileFlyonUi background="info-container" content="info-container-content" />
                            <ColorTileFlyonUi background="info-container-content" content="info-container" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="success-container" content="success-container-content" />
                            <ColorTileFlyonUi background="success-container-content" content="success-container" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="warning-container" content="warning-container-content" />
                            <ColorTileFlyonUi background="warning-container-content" content="warning-container" />
                        </div>
                        <div>
                            <ColorTileFlyonUi background="error-container" content="error-container-content" />
                            <ColorTileFlyonUi background="error-container-content" content="error-container" />
                        </div>
						<p class="text-2xl">TBD: Others: background and more</p>
                        <div>surface container low - between b1 and b2</div>
						<div>surface container high - between b2 and b3</div>
						<div>on surface variant</div>
						<div>outline</div>
						<div>outline variant</div>
						<div>inverse surface</div>
						<div>inverse on surface</div>
						<div>inverse primary</div>
						<div>scrim</div>
						<div>background - might not be necessary?</div>
						<div>on background</div>
						<div>neutral palette key color - not the neutral from above, as the color input is coming from flyonUI, but this one is material designs own</div>
						<div>neutral variant palette key color</div>
						<p class="text-2xl">Avoid the following - fixed is not switching between light and dark</p>
						<div>primary fixed</div>
						<div>primary variant dim</div>
						<div>on primary variant</div>
						<div>on primary fixed variant</div>
						<div>secondary fixed</div>
						<div>secondary fixed dim</div>
						<div>on secondary fixed</div>
						<div>on secondary fixed variant</div>
						<div>tertiary fixed</div>
						<div>tertiary fixed dim</div>
						<div>on tertiary fixed</div>
						<div>on tertiary fixed variant</div>
						<div>surface dim</div>
						<div>surface</div>
						<div>surface bright</div>
						<div>surface variant</div>
						<div>surface tint</div>
                    </div>
                </div>
            </div>
        </div>
	</div>
	<div class="col-span-2">
		<p class="italic text-xl">Note, for programmatically applied classes, add the utility class also programmatically via <code>Theming.addUtilityClass( className, styles)</code> </p>
	</div>

	<div class="col-span-2">
		<Title>Utility classes</Title>
		<div>Mainly playing with:
			<ul>
				<li>primary (native in both FlyonUI and Material Design),</li>
				<li>inverse primary (native only in Material Design),</li>
				<li>surface tint (avoid using),</li>
				<li>error (also native in both - showing it works)</li>
				<li>error/50 (checking transparency from Tailwind)</li>
			</ul>
		</div>
		<div class="w-full mt-5 grid grid-cols-5 gap-4">
			<div class="ml-5 col-span-5 text-2xl font-semibold">bg-"COLOR-NAME"</div>
			<div class="bg-primary h-24">bg-primary</div>
			<div class="bg-inverse-primary h-24">bg-inverse-primary</div>
			<div class="bg-surface-tint h-24">bg-surface-tint</div>
			<div class="bg-error h-24">bg-error</div>
			<div class="bg-error/50 h-24">bg-error/50</div>

			<div class="ml-5 col-span-5 text-2xl font-semibold">from-"COLOR-NAME" via-"COLOR-NAME" to-"COLOR-NAME"</div>
			<div class="bg-gradient-to-r from-primary via-secondary to-accent h-24">from-primary via-scondary to-accent</div>
			<div class="bg-gradient-to-r from-success via-warning to-error h-24">from-success via-warning to-error</div>
			<div class="bg-gradient-to-r from-success via-warning to-error bg-clip-text text-transparent font-black text-xl w-fit h-24">from-success via-warning to-error applied to text</div>
			<div class="bg-gradient-to-r from-primary via-inverse-primary to-surface-tint h-24">from-primary via-inverse-primary to-surface-tint</div>
			<div class="bg-gradient-to-r from-primary/50 via-secondary/50 to-accent/50 h-24">from-primary/50 via-scondary/50 to-accent/50</div>
			
			<div class="ml-5 col-span-5 text-2xl font-semibold">text-"COLOR-NAME"</div>
			<div class="text-primary text-4xl font-bold h-24 ">text-primary</div>
			<div class="text-inverse-primary text-4xl font-bold h-24">text-inverse-primary</div>
			<div class="text-surface-tint text-4xl font-bold h-24">text-surface-tint</div>
			<div class="text-error text-4xl font-bold h-24">text-error</div>
			<div class="text-error/50 text-4xl font-bold h-24">text-error/50</div>

			<div class="ml-5 col-span-5 text-2xl font-semibold">ring-"COLOR-NAME"</div>
			<div><input type="radio" name="radioPrimary" class="radio radio-primary" id="radioPrimary" checked/>Radio primary</div>
			<div><input type="radio" name="radioInversePrimary" class="radio radio-inverse-primary" id="radioInversePrimary" checked/>Radio inverse primary</div>
			<div><input type="radio" name="radioSurfaceTint" class="radio radio-surface-tint" id="radioSurfaceTint" checked/>Radio surface tint</div>
			<div><input type="radio" name="radioError" class="radio radio-error" id="radioError" checked/>Radio error</div>
			<div><input type="radio" name="radioError50" class="radio radio-error/50" id="radioError50" checked/>Radio error/50</div>
			<button class="button ring ring-primary">ring-primary</button>
			<button class="button ring ring-inverse-primary">ring-inverse-primary</button>
			<button class="button ring ring-surface-tint">ring-surface-tint</button>
			<button class="button ring ring-error">ring-error</button>
			<button class="button ring ring-error/50">ring-error/50</button>

			<div class="ml-5 col-span-5 text-2xl font-semibold">fill-"COLOR-NAME"</div>
			<svg class="fill-primary h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"></path></svg>
			<svg class="fill-inverse-primary h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"></path></svg>
			<svg class="fill-surface-tint h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"></path></svg>
			<svg class="fill-error h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"></path></svg>
			<svg class="fill-error/50 h-14" viewBox="0 0 46 48" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M23.0002 0C12.5068 0 4.00017 8.50659 4.00017 19V32.5335C4.00017 32.8383 3.9145 33.1371 3.75292 33.3956L0.912672 37.94C0.0801118 39.2721 1.0378 41 2.60867 41H43.3917C44.9625 41 45.9202 39.2721 45.0877 37.94L42.2474 33.3956C42.0858 33.1371 42.0002 32.8383 42.0002 32.5335V19C42.0002 8.50659 33.4936 0 23.0002 0ZM23.0002 48C20.2388 48 18.0002 45.7614 18.0002 43H28.0002C28.0002 45.7614 25.7616 48 23.0002 48Z"></path></svg>
			
			<div class="ml-5 col-span-5 text-2xl font-semibold">caret-"COLOR-NAME"</div>
			<textarea class="caret-primary h-24">caret-primary: cursor color!</textarea>
			<textarea class="caret-inverse-primary h-24">caret-invserse-primary: cursor color!</textarea>
			<textarea class="caret-surface-tint h-24">caret-surface-tint: cursor color!</textarea>
			<textarea class="caret-error h-24">caret-error: cursor color!</textarea>
			<textarea class="caret-error/50 h-24">caret-error/50: cursor color!</textarea>
			
			<div class="ml-5 col-span-5 text-2xl font-semibold">stroke-"COLOR-NAME"</div>
			<svg class="stroke-primary h-10" viewBox="0 0 48 40" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z" stroke-width="2"></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>
			<svg class="stroke-inverse-primary h-10" viewBox="0 0 48 40" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z" stroke-width="2"></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>
			<svg class="stroke-surface-tint h-10" viewBox="0 0 48 40" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z" stroke-width="2"></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>
			<svg class="stroke-error h-10" viewBox="0 0 48 40" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z" stroke-width="2"></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>
			<svg class="stroke-error/50 h-10" viewBox="0 0 48 40" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M1 13C1 10.2386 3.23858 8 6 8H13.4914C14.3844 8 15.1691 7.40805 15.4144 6.54944L16.5856 2.45056C16.8309 1.59196 17.6156 1 18.5086 1H29.4914C30.3844 1 31.1691 1.59195 31.4144 2.45056L32.5856 6.54944C32.8309 7.40804 33.6156 8 34.5086 8H42C44.7614 8 47 10.2386 47 13V34C47 36.7614 44.7614 39 42 39H6C3.23858 39 1 36.7614 1 34V13Z" stroke-width="2"></path> <circle cx="24" cy="23" r="9" stroke-width="2"></circle>
			</svg>


			<div class="ml-5 col-span-5 text-2xl font-semibold">border-"COLOR-NAME"</div>
			<div class="border-4 border-primary h-24">border-primary</div>
			<div class="border-4 border-inverse-primary h-24">border-inverse-primary</div>
			<div class="border-4 border-surface-tint h-24">border-surface-tint</div>
			<div class="border-4 border-error h-24">border-error</div>
			<div class="border-4 border-error/50 h-24">border-error/50</div>

			<div class="ml-5 col-span-5 text-2xl font-semibold">divide-"COLOR-NAME"</div>
			<div class="divide-y divide-primary h-24"><div>divide</div><div>between</div><div>elements</div></div>
			<div class="divide-y divide-inverse-primary h-24"><div>divide</div><div>between</div><div>elements</div></div>
			<div class="divide-y divide-surface-tint h-24"><div>divide</div><div>between</div><div>elements</div></div>
			<div class="divide-y divide-error h-24"><div>divide</div><div>between</div><div>elements</div></div>
			<div class="divide-y divide-error/50 h-24"><div>divide</div><div>between</div><div>elements</div></div>

			<div class="ml-5 col-span-5 text-2xl font-semibold">accent-"COLOR-NAME"</div>
			<label>
				<input type="checkbox" class="accent-primary" checked> primary
			</label>
			<label>
				<input type="checkbox" class="accent-inverse-primary" checked> inverse primary
			</label>
			<label>
				<input type="checkbox" class="accent-surface-tint" checked> surface tint
			</label>
			<label>
				<input type="checkbox" class="accent-error" checked> error
			</label>
			<label>
				<input type="checkbox" class="accent-error/50" checked> error/50
			</label>
			<label>
				<input type="checkbox" class="checkbox checkbox-primary" checked> primary
			</label>
			<label>
				<input type="checkbox" class="checkbox checkbox-inverse-primary" checked> inverse primary
			</label>
			<label>
				<input type="checkbox" class="checkbox checkbox-surface-tint" checked> surface tint
			</label>
			<label>
				<input type="checkbox" class="checkbox checkbox-error" checked> error
			</label>
			<label>
				<input type="checkbox" class="checkbox checkbox-error/50" checked> error/50
			</label>

			<div class="ml-5 col-span-5 text-2xl font-semibold">shadow-"COLOR-NAME"</div>
			<button class="btn btn-primary shadow-lg shadow-primary">Shadow primary</button>
			<button class="btn btn-inverse-primary shadow-lg shadow-inverse-primary">Shadow inverse primary</button>
			<button class="btn btn-surface-tint shadow-lg shadow-surface-tint">Shadow surface tint</button>
			<button class="btn btn-error shadow-lg shadow-error">Shadow error</button>
			<button class="btn btn-error/50 shadow-lg shadow-error/50">Shadow error/50</button>


			<div class="ml-5 col-span-5 text-2xl font-semibold">outline-"COLOR-NAME"</div>
			<button class="btn btn-outline btn-primary">primary</button>
			<button class="btn btn-outline btn-inverse-primary">inverse primary</button>
			<button class="btn btn-outline btn-surface-tint">surface tint</button>
			<button class="btn btn-outline btn-error">error</button>
			<button class="btn btn-outline btn-error/50">error/50</button>
			<div class="flex items-center gap-1">
				<input type="checkbox" class="switch switch-outline switch-primary" id="switchPrimary" />
				<label class="label label-text text-base" for="switchPrimary"> Default </label>
			</div>
			<div class="flex items-center gap-1">
				<input type="checkbox" class="switch switch-outline switch-inverse-primary" id="switchInversePrimary" />
				<label class="label label-text text-base" for="switchInversePrimary"> Inverse </label>
			</div>
			<div class="flex items-center gap-1">
				<input type="checkbox" class="switch switch-outline switch-surface-tint" id="switchSurfaceTint" />
				<label class="label label-text text-base" for="switchSurfaceTint"> Surface tint </label>
			</div>
			<div class="flex items-center gap-1">
				<input type="checkbox" class="switch switch-outline switch-error" id="switchError" />
				<label class="label label-text text-base" for="switchError"> Error </label>
			</div>
			<div class="flex items-center gap-1">
				<input type="checkbox" class="switch switch-outline switch-error/50" id="switchError50" />
				<label class="label label-text text-base" for="switchError50"> Error/50 </label>
			</div>


			<div class="ml-5 col-span-5 text-2xl font-semibold">decoration-"COLOR-NAME"</div>
			<div class="underline decoration-primary h-24">decoration-primary</div>
			<div class="underline decoration-inverse-primary h-24">decoration-inverse-primary</div>
			<div class="underline decoration-surface-tint h-24">decoration-surface-tint</div>
			<div class="underline decoration-error h-24">decoration-error</div>
			<div class="underline decoration-error/50 h-24">decoration-error/50</div>

			<div class="ml-5 col-span-5 text-2xl font-semibold">placeholder-"COLOR-NAME"</div>
			<label class="relative block">
				<input class="input placeholder:text-primary" placeholder="Placeholder primary" type="text" name="search"/>
			</label>
			<label class="relative block">
				<input class="input placeholder:text-inverse-primary" placeholder="Placeholder inverse primary" type="text" name="search"/>
			</label>
			<label class="relative block">
				<input class="input placeholder:text-surface-tint" placeholder="Placeholder surface tint" type="text" name="search"/>
			</label>
			<label class="relative block">
				<input class="input placeholder:text-error" placeholder="Placeholder error" type="text" name="search"/>
			</label>
			<label class="relative block">
				<input class="input placeholder:text-error/50" placeholder="Placeholder error/50" type="text" name="search"/>
			</label>

			<div class="ml-5 col-span-5 text-2xl font-semibold">ring-offset-"COLOR-NAME"</div>
			<span class="badge ring-2 ring-red-300 ring-offset-4 ring-offset-primary">primary</span>
			<span class="badge ring-2 ring-red-300 ring-offset-4 ring-offset-inverse-primary">inverse primary</span>
			<span class="badge ring-2 ring-red-300 ring-offset-4 ring-offset-surface-tint">surface tint</span>
			<span class="badge ring-2 ring-blue-300 ring-offset-4 ring-offset-error">error</span>
			<span class="badge ring-2 ring-blue-300 ring-offset-4 ring-offset-error/50">error/50</span>
		</div>
	</div>

	<div>
		<Title>Components with utility classes</Title>
		<p>Badges:</p>
		<span class="badge badge-primary">Badge primary</span>
		<span class="badge badge-secondary">Badge secondary</span>
		<span class="badge badge-tertiary">Badge tertiary (Material notation)</span>
		<span class="badge badge-accent">Badge accent (same in FlyonUI notation)</span>
		<br />
	</div>

	<div>
		<Title>Typography</Title>
		<link rel="preconnect" href="https://fonts.googleapis.com" />
		<p>Fonts:</p>
		<p class="font-sans">
			Some text in <em>sans</em> font family, should be using <b>Robot</b> Google Fonts extending
			default theme in <code>tailwindcss.config.js</code>.
		</p>
		<p class="font-serif">
			Some text in <em>serif</em> font family, should be using <b>Merriweather</b> Google Fonts,
			extending default theme in <code>tailwindcss.config.js</code>.
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
		<p class="text-center text-xl">Iconify with FlyonUI</p>
		<div class="grid grid-cols-5 gap-4">
			<div>
				<p class="text-center text-xl">Default library "tablers"</p>
				<span class="icon-[tabler--settings] size-12"></span>
				<span class="icon-[tabler--palette] size-12"></span>
				<span class="icon-[tabler--home] size-12"></span>
				<span class="icon-[tabler--user] size-12"></span>
			</div>
			<div>
				<p class="text-center text-xl">Extension library "Material Symbols"</p>
				<span class="icon-[material-symbols--settings-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--palette-outline] size-12"></span>
				<span class="icon-[material-symbols--home-outline-rounded] size-12"></span>
				<span class="icon-[material-symbols--person-outline-rounded] size-12"></span>
			</div>
			<div>
				<p class="text-center text-xl">Extension library "SVG spinners"</p>
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
				<p class="text-center text-xl">Extension library "Font Awesome Solid</p>
				<span class="icon-[fa6-solid--droplet] size-12"></span>
				<span class="icon-[fa6-solid--comments] size-12"></span>
				<p class="text-center text-xl">Extension library "Font Awesome Brands</p>
				<span class="icon-[fa6-brands--discord] size-12"></span>
				<span class="icon-[fa6-brands--youtube] size-12"></span>
				<span class="icon-[fa6-brands--linux] size-12"></span>
				<span class="icon-[fa6-brands--github] size-12"></span>
			</div>
			<div>
				<p class="text-center text-xl">Extension library "Noto emoji</p>
				<span class="icon-[noto--folded-hands] size-12"></span>
				<span class="icon-[noto--folded-hands-medium-dark-skin-tone] size-12"></span>
				<span class="icon-[noto--heart-hands] size-12"></span>
				<span class="icon-[noto--heart-hands-dark-skin-tone] size-12"></span>
				<span class="icon-[noto--fire] size-12"></span>
				<span class="icon-[noto--smiling-face-with-sunglasses] size-12"></span>
				<span class="icon-[noto--check-mark-button] size-12"></span>
				<span class="icon-[noto--cross-mark] size-12"></span>
			</div>
		</div>
	</div>

	<div>
		<Title>Theme Picker</Title>
		<div class="grid grid-cols-3 gap-4">
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
				<div class="modal-content bg-base-300">
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
