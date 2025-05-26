<script lang="ts">
	import { page } from '$app/state';
	import NavigationCard from '$components/NavigationCard.svelte';
	import Heading from '$components/Heading.svelte';
	import AccordionItem from './AccordionItem.svelte';
	import ColorTile from './ColorTile.svelte';

	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);

	const backgrounds = ['background', 'base-100', 'base-150', 'base-200', 'base-250', 'base-300'];
	const components = [
		'primary',
		'secondary',
		'accent',
		'neutral',
		'info',
		'success',
		'warning',
		'error'
	];

	const backgroundSelection = {
		background: 0,
		foreground: true,
		component: 0,
		outline: false,
		shadow: false
	}

	let playgroundSelections = $state([backgroundSelection]);

	const addPlayground = () => { playgroundSelections.push( backgroundSelection ); };

	let playgrounds = $derived(
		playgroundSelections.map( (selection) => {
			return {
				background: backgrounds[selection.background],
				foreground: selection.foreground ? 'base-content' : 'base-content-variant',
				component: components[selection.component],
				outline: selection.outline ? 'outline' : '',
				shadow: selection.shadow ? 'base-shadow' : ''
			};
		})
	);
</script>

<Heading>🚧 Construction sites - for design experiments 🚧</Heading>

<div class="mb-5 grid grid-cols-1 gap-8 md:grid-cols-3">
	<NavigationCard title="FlyonUI 1" href="/playground/design/flyonui">
		"Playground and showcase for flyonUI components and design"
	</NavigationCard>
	<NavigationCard title="Material Design 3" href="/playground/design/materialdesign">
		Playground and showcase for Material Design 3 components and design
	</NavigationCard>
	<NavigationCard title="TailwindCSS 3" href="/playground/design/tailwindcss">
		Formating playground for styling with TailwindCSS utility classes
	</NavigationCard>
	<NavigationCard title="Comparison" href="/playground/design/comparison">
		Directly putting components right next to each other to compare them
	</NavigationCard>
	<NavigationCard title="Playground" href="#playground">
		Play with the colors and some components below to get a preview of the design
	</NavigationCard>
</div>

<Heading>👍 Results - ready for use 👍</Heading>
<div class="mb-2 flex items-center gap-1">
	<label class="label label-text text-base" for="debugSwitcher">Debug: </label>
	<input type="checkbox" class="switch-neutral switch" bind:checked={debug} id="debugSwitcher" />
</div>

<p class="text-base-content">
	The following is the result of applying Material Design 3 to FlyonUI 2, based on Tailwind CSS 4.
	It applies the color philosophy from Material Design to the theming of FlyonUI and Tailwind CSS.
</p>
<p class="text-base-content">
	Turn on debug to get the names of teh CSS variables and the color values.
</p>

<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="">
	<AccordionItem title="Backgrounds and Surfaces">
		<p>
			Background is the very background of the page. The base colors provide backgrounds to larger
			surfaces, like navigation elements and larger windows. The further upfront the more they
			contrast from the background.
		</p>
		<div class="hidden md:block">
			<ColorTile background="background" text="base-content" {debug}
				>The background color of the <code class="font-mono">body</code> of the page.</ColorTile
			>
		</div>
		<div class="grid grid-cols-3 md:grid-cols-5">
			<div class="block md:hidden">
				<ColorTile background="background" text="base-content" {debug}
					>The background color of the <code class="font-mono">body</code> of the page.</ColorTile
				>
			</div>
			<ColorTile background="base-100" text="base-content" {debug}
				>Lowest container surface</ColorTile
			>
			<ColorTile background="base-150" text="base-content" {debug}>Low container surface</ColorTile>
			<ColorTile background="base-200" text="base-content" {debug}
				>Medium container surface</ColorTile
			>
			<ColorTile background="base-250" text="base-content" {debug}>High container surface</ColorTile
			>
			<ColorTile background="base-300" text="base-content" {debug}
				>Highest container surface</ColorTile
			>
		</div>
	</AccordionItem>
	<AccordionItem title="Foregrounds">
		<p>Foregrounds are the default colors for text on background and surfaces.</p>
		<div class="grid grid-cols-2">
			<ColorTile background="base-content" text="background" {debug}
				>Used for all text, that is directly on the background and in larger sections of surfaces
				(base-colors)</ColorTile
			>
			<ColorTile background="base-content-variant" text="background" {debug}
				>An alternative to base-content.</ColorTile
			>
		</div>
	</AccordionItem>
	<AccordionItem title="Components">
		<p>
			Coloring components according to their meaning, preferably against <code>base</code> surfaces.
		</p>
		<div class="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-8">
			<div class="bg-primary-container/40 m-1 rounded-2xl">
				<p class="title text-primary-container-content text-center">Primary</p>
				<p
					class="body-small text-primary-container-content mb-4 h-24 overflow-auto p-2 text-justify md:h-30"
				>
					Key components like "OK" buttons.
				</p>
				<ColorTile background="primary" text="primary-content" {debug} />
				<ColorTile background="primary-content" text="primary" {debug} />
				<ColorTile background="primary-container" text="primary-container-content" {debug} />
				<ColorTile background="primary-container-content" text="primary-container" {debug} />
			</div>
			<div class="bg-secondary-container/40 m-1 rounded-2xl">
				<p class="title text-secondary-container-content text-center">Secondary</p>
				<p
					class="body-small text-secondary-container-content mb-4 h-24 overflow-auto p-2 text-justify md:h-30"
				>
					Less prominent components like "cancel" buttons.
				</p>
				<ColorTile background="secondary" text="secondary-content" {debug} />
				<ColorTile background="secondary-content" text="secondary" {debug} />
				<ColorTile background="secondary-container" text="secondary-container-content" {debug} />
				<ColorTile background="secondary-container-content" text="secondary-container" {debug} />
			</div>
			<div class="bg-accent-container/40 m-1 rounded-2xl">
				<p class="title text-accent-container-content text-center">Accent</p>
				<p
					class="body-small text-accent-container-content mb-4 h-24 overflow-auto p-2 text-justify md:h-30"
				>
					Attention seeking, like "notification" badges.
				</p>
				<ColorTile background="accent" text="accent-content" {debug} />
				<ColorTile background="accent-content" text="accent" {debug} />
				<ColorTile background="accent-container" text="accent-container-content" {debug} />
				<ColorTile background="accent-container-content" text="accent-container" {debug} />
			</div>
			<div class="bg-neutral-container/40 m-1 rounded-2xl">
				<p class="title text-neutral-container-content text-center">Neutral</p>
				<p
					class="body-small text-neutral-container-content mb-4 h-24 overflow-auto p-2 text-justify md:h-30"
				>
					Elements that are similar to primary - use for distinguishing between content and app
					interaction / navigation.
				</p>
				<ColorTile background="neutral" text="neutral-content" {debug} />
				<ColorTile background="neutral-content" text="neutral" {debug} />
				<ColorTile background="neutral-container" text="neutral-container-content" {debug} />
				<ColorTile background="neutral-container-content" text="neutral-container" {debug} />
			</div>
			<div class="bg-info-container/40 m-1 rounded-2xl">
				<p class="title text-info-container-content text-center">Info</p>
				<p
					class="body-small text-info-container-content mb-4 h-24 overflow-auto p-2 text-justify md:h-30"
				>
					Information towards the user - especially in connection with user input.
				</p>
				<ColorTile background="info" text="info-content" {debug} />
				<ColorTile background="info-content" text="info" {debug} />
				<ColorTile background="info-container" text="info-container-content" {debug} />
				<ColorTile background="info-container-content" text="info-container" {debug} />
			</div>
			<div class="bg-success-container/40 m-1 rounded-2xl">
				<p class="title text-success-container-content text-center">Success</p>
				<p
					class="body-small text-success-container-content mb-4 h-24 overflow-auto p-2 text-justify md:h-30"
				>
					Feedback to user after successful action.
				</p>
				<ColorTile background="success" text="success-content" {debug} />
				<ColorTile background="success-content" text="success" {debug} />
				<ColorTile background="success-container" text="success-container-content" {debug} />
				<ColorTile background="success-container-content" text="success-container" {debug} />
			</div>
			<div class="bg-warning-container/40 m-1 rounded-2xl">
				<p class="title text-warning-container-content text-center">Warning</p>
				<p
					class="body-small text-warning-container-content mb-4 h-24 overflow-auto p-2 text-justify md:h-30"
				>
					Seeking caution after user interaction.
				</p>
				<ColorTile background="warning" text="warning-content" {debug} />
				<ColorTile background="warning-content" text="warning" {debug} />
				<ColorTile background="warning-container" text="warning-container-content" {debug} />
				<ColorTile background="warning-container-content" text="warning-container" {debug} />
			</div>
			<div class="bg-error-container/40 m-1 rounded-2xl">
				<p class="title text-error-container-content text-center">Error</p>
				<p
					class="body-small text-error-container-content mb-4 h-24 overflow-auto p-2 text-justify md:h-30"
				>
					Informing user of error, especially after user interaction.
				</p>
				<ColorTile background="error" text="error-content" {debug} />
				<ColorTile background="error-content" text="error" {debug} />
				<ColorTile background="error-container" text="error-container-content" {debug} />
				<ColorTile background="error-container-content" text="error-container" {debug} />
			</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Outlines and others">
		<p>For borders, rings, shadows and anything else around components</p>
		<div class="grid grid-cols-2 md:grid-cols-4">
			<ColorTile background="outline" text="base-content" {debug}
				>Important boundaries to mark a clear box.</ColorTile
			>
			<ColorTile background="outline-variant" text="base-content" {debug}
				>Supportive boundaries, like dividers - where other elements provide visual boundaries</ColorTile
			>
			<ColorTile background="base-shadow" text="white" {debug}>Shadow for containers.</ColorTile>
			<ColorTile background="scrim" text="white" {debug}
				>Overlay of content behind navigation elements and modals to draw attention to the pop-over
				element</ColorTile
			>
		</div>
	</AccordionItem>
	<AccordionItem title="Inverse" active={false}>
		<p>
			If in dark mode, the color would be like this in light mode and vice versa. Avoid using them.
		</p>
		<div class="grid grid-cols-3">
			<ColorTile background="inverse-surface" text="inverse-surface-content" {debug} />
			<ColorTile background="inverse-surface-content" text="inverse-surface" {debug} />
			<ColorTile background="inverse-primary" text="base-content" {debug} />
		</div>
	</AccordionItem>
	<AccordionItem title="Fixed" active={false}>
		<p>Those colors don't change when switching from light mode to dark mode. Avoid using them.</p>
		<div class="grid grid-cols-3">
			<div class="bg-primary-fixed/40 rounded-2xl">
				<p class="title text-primary-fixed-content text-center">Primary-fixed</p>
				<ColorTile background="primary-fixed" text="primary-fixed-content" {debug} />
				<ColorTile background="primary-fixed-dim" text="primary-fixed-content" {debug} />
				<ColorTile background="primary-fixed-content" text="primary-fixed" {debug} />
				<ColorTile background="primary-fixed-variant-content" text="primary-fixed" {debug} />
			</div>
			<div class="bg-secondary-fixed/40 rounded-2xl">
				<p class="title text-secondary-fixed-content text-center">Secondary-fixed</p>
				<ColorTile background="secondary-fixed" text="secondary-fixed-content" {debug} />
				<ColorTile background="secondary-fixed-dim" text="secondary-fixed-content" {debug} />
				<ColorTile background="secondary-fixed-content" text="secondary-fixed" {debug} />
				<ColorTile background="secondary-fixed-variant-content" text="secondary-fixed" {debug} />
			</div>
			<div class="bg-accent-fixed/40 rounded-2xl">
				<p class="title text-accent-fixed-content text-center">Accent-fixed</p>
				<ColorTile background="accent-fixed" text="accent-fixed-content" {debug} />
				<ColorTile background="accent-fixed-dim" text="accent-fixed-content" {debug} />
				<ColorTile background="accent-fixed-content" text="accent-fixed" {debug} />
				<ColorTile background="accent-fixed-variant-content" text="accent-fixed" {debug} />
			</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Palette key and surface" active={false}>
		<p>Of no technical use any more. Avoid using them.</p>
		<div class="grid grid-cols-2 md:grid-cols-5">
			<ColorTile background="primary-palette-key-color" text="base-content" {debug} />
			<ColorTile background="secondary-palette-key-color" text="background" {debug} />
			<ColorTile background="accent-palette-key-color" text="inverse-surface-content" {debug} />
			<ColorTile background="neutral-palette-key-color" text="inverse-surface-content" {debug} />
			<ColorTile
				background="neutral-variant-palette-key-color"
				text="inverse-surface-content"
				{debug}
			/>
		</div>
		<div class="grid grid-cols-2 md:grid-cols-5">
			<ColorTile background="surface-dim" text="base-content" {debug} />
			<ColorTile background="surface" text="base-content" {debug} />
			<ColorTile background="surface-bright" text="base-content" {debug} />
			<ColorTile background="surface-variant" text="base-content" {debug} />
			<ColorTile background="surface-tint" text="inverse-surface-content" {debug} />
		</div>
	</AccordionItem>
</div>

<div
	class="mt-5 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 h-screen min-h-fit w-full gap-4"
	id="playground"
>
	<div class="heading grow w-full col-span-full">Playground to preview color combinations</div>
	{#each playgrounds as playground, i (i)}
		<div class="w-full flex flex-row flex-wrap gap-2 bg-{playground.background} text-{playground.foreground} {playground.outline} {playground.shadow ? 'shadow-2xl shadow-base-shadow' : ''} rounded-3xl p-4">
			<div class="w-96">
				<label class="label label-text" for="background"
					>Background: <span class="label">
						<code class="label-text-alt">{playground.background}</code>
					</span></label
				>
				<input
					type="range"
					min="0"
					max="5"
					step="1"
					class="range w-full"
					aria-label="contrast"
					id="contrast"
					bind:value={playgroundSelections[i].background}
				/>
				<div class="flex w-full justify-between px-2 text-xs">
					<div><span class="mr-9">default</span><span>less</span></div>
					<div>more</div>
					<!-- {#each backgrounds as background,i (i)}
					<div class="grid grid-cols-1 w-full">
						<span class="w-full justify-center">|</span>
						<span>{background}</span>
					</div>
					{/each} -->
				</div>
			</div>
			<div class="w-64">
				<label class="label label-text text-base" for="foreground">Foreground:</label>
				<input
					type="checkbox"
					class="switch switch-{playground.component} text-center"
					bind:checked={playgroundSelections[i].foreground}
					id="foreground"
				/>
				<code class="label-text-alt">{playground.foreground}</code>
			</div>
			<div class="w-36">
				<label class="label label-text" for="component">Component</label>
				<select
					class="select select-floating select-{playground.component} h-12 max-w-sm"
					aria-label="Select variant"
					id="themeVariant"
					bind:value={playgroundSelections[i].component}
				>
					{#each components as component, i (i)}
						<option value={i}>{component}</option>
					{/each}
				</select>
			</div>
			<div class="w-24">
				<label class="label label-text text-base" for="outline">Outline:</label>
				<input
					type="checkbox"
					class="switch switch-{playground.component} text-center"
					bind:checked={playgroundSelections[i].outline}
					id="foreground"
				/>
				<code class="label-text-alt">{playground.outline ? "on" : "off"}</code>
			</div>
			<div class="w-24">
				<label class="label label-text text-base" for="outline">Shadow:</label>
				<input
					type="checkbox"
					class="switch switch-{playground.component} text-center"
					bind:checked={playgroundSelections[i].shadow}
					id="foreground"
				/>
				<code class="label-text-alt">{playground.shadow ? "on" : "off"}</code>
			</div>
			<div>
				<div class="heading">Heading</div>
				<div class="title">Some title here</div>
				<div class="body">
					This is a bunch of body text on top of the selected background, using the selected
					foreground.
				</div>
				<div class="divider-outline-variant divider my-2"></div>
				<div class="body-small">
					The divider below always uses outline-variant.
				</div>
				<div class="divider-outline-variant divider my-2"></div>
				<div class="body-small">
					The shadow in in the components is an inner shadow.
				</div>
				<div class="flex grow  flex-wrap gap-4 {playground.outline} rounded-2xl {playground.shadow ? 'shadow-xl shadow-base-shadow' : ''} m-2 p-4 mb-5">
					<div class="title-small text-center font-bold text-{playground.component}">
						Using component color
					</div>
					<div class="input-filled input-{playground.component} w-100 grow rounded-md {playground.shadow ? 'shadow-inner shadow-base-shadow' : ''}">
						<input type="text" placeholder="colored input" class="input" id="playgroundInput" />
						<label class="input-filled-label" for="playgroundInput">Text input</label>
					</div>
					<button
						class="label-small md:label btn btn-{playground.component} max-w-36 rounded-full {playground.shadow ? 'shadow-inner shadow-base-shadow' : ''}">Component</button
					>
					<button
						class="badge badge-{playground.component}-container label-small h-8 rounded-3xl lg:rounded-full {playground.shadow ? 'shadow-inner shadow-base-shadow' : ''}">Container</button
					>
					<button
						class="btn-{playground.component}-container btn btn-circle btn-gradient" aria-label="Add Icon Button"
					><span class="icon-[fa6-solid--plus]"></span></button
				>
				</div>
			</div>
		</div>
	{/each}
	<button class="w-full label btn btn-primary rounded-full m-4" onclick={addPlayground}><span class="icon-[fa6-solid--plus]"></span> Add playground</button>
</div>

<p>
	Add a playground here for text fields and buttons with ruler for background, dropdown for
	foreground and checkboxes for shadow and outline.
</p>
