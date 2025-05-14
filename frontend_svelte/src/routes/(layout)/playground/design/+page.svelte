<script lang="ts">
	import { page } from '$app/state';
	import NavigationCard from '$components/NavigationCard.svelte';
	import Heading from '$components/Heading.svelte';
	import AccordionItem from './AccordionItem.svelte';
	import ContentText from './ContentText.svelte';
	import AppText from './AppText.svelte';
	import ContentInteraction from './ContentInteraction.svelte';
	import AppInteraction from './AppInteraction.svelte';
	import BackgroundRows from './BackgroundRows.svelte';
	import Containers from './Containers.svelte';
	import ColorTile from './ColorTile.svelte';

	let debug = $state(page.url.searchParams.get('debug') === 'true' ? true : false);
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
		<p>Coloring components according to their meaning.</p>
		<div class="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-8">
			<div>
				<p class="title text-primary text-center">Primary</p>
				<ColorTile background="primary" text="primary-content" {debug} />
				<ColorTile background="primary-content" text="primary" {debug} />
				<ColorTile background="primary-container" text="primary-container-content" {debug} />
				<ColorTile background="primary-container-content" text="primary-container" {debug} />
			</div>
			<div>
				<p class="title text-secondary text-center">Secondary</p>
				<ColorTile background="secondary" text="secondary-content" {debug} />
				<ColorTile background="secondary-content" text="secondary" {debug} />
				<ColorTile background="secondary-container" text="secondary-container-content" {debug} />
				<ColorTile background="secondary-container-content" text="secondary-container" {debug} />
			</div>
			<div>
				<p class="title text-accent text-center">Accent</p>
				<ColorTile background="accent" text="accent-content" {debug} />
				<ColorTile background="accent-content" text="accent" {debug} />
				<ColorTile background="accent-container" text="accent-container-content" {debug} />
				<ColorTile background="accent-container-content" text="accent-container" {debug} />
			</div>
			<div>
				<p class="title text-neutral text-center">Neutral</p>
				<ColorTile background="neutral" text="neutral-content" {debug} />
				<ColorTile background="neutral-content" text="neutral" {debug} />
				<ColorTile background="neutral-container" text="neutral-container-content" {debug} />
				<ColorTile background="neutral-container-content" text="neutral-container" {debug} />
			</div>
			<div>
				<p class="title text-info text-center">Info</p>
				<ColorTile background="info" text="info-content" {debug} />
				<ColorTile background="info-content" text="info" {debug} />
				<ColorTile background="info-container" text="info-container-content" {debug} />
				<ColorTile background="info-container-content" text="info-container" {debug} />
			</div>
			<div>
				<p class="title text-success text-center">Success</p>
				<ColorTile background="success" text="success-content" {debug} />
				<ColorTile background="success-content" text="success" {debug} />
				<ColorTile background="success-container" text="success-container-content" {debug} />
				<ColorTile background="success-container-content" text="success-container" {debug} />
			</div>
			<div>
				<p class="title text-warning text-center">Warning</p>
				<ColorTile background="warning" text="warning-content" {debug} />
				<ColorTile background="warning-content" text="warning" {debug} />
				<ColorTile background="warning-container" text="warning-container-content" {debug} />
				<ColorTile background="warning-container-content" text="warning-container" {debug} />
			</div>
			<div>
				<p class="title text-error text-center">Error</p>
				<ColorTile background="error" text="error-content" {debug} />
				<ColorTile background="error-content" text="error" {debug} />
				<ColorTile background="error-container" text="error-container-content" {debug} />
				<ColorTile background="error-container-content" text="error-container" {debug} />
			</div>
		</div>
		<p>
			Add a playground here for text fields and buttons with ruler for background, dropdown for
			foreground and checkboxes for shadow and outline.
		</p>
	</AccordionItem>
	<AccordionItem title="Outlines and others">
		<p>outline, outline-variant, base-shadow</p>
	</AccordionItem>
	<AccordionItem title="Inverse">
		<p>
			If in dark mode, the color would be like this in light mode and vice verse: inverse-surface,
			inverse-surface-content, inverse-primary
		</p>
	</AccordionItem>
	<AccordionItem title="Fixed">
		<p>
			Don't change color from light mode to dark mode: primary-fixed, primary-fixed-dim,
			primary-fixed-content, primary-fixed-variant-content
		</p>
		<p>Same for secondary and accent.</p>
		<p>Avoid using those!</p>
	</AccordionItem>
	<AccordionItem title="Palette key and surface">
		<p>Of no technical use any more:</p>
		<p>
			neutral-palette-key, neutral-variant-palette-key, primary-palette-key, secondary-palette-key,
			accent-palette-key
		</p>
		<p>surface-dim, surface, surface-bright, surface-variant, surface-tint</p>
	</AccordionItem>
	<AccordionItem title="Backgrounds old">
		<div class="bg-background text-base-content flex h-screen min-h-fit w-full flex-col">
			<div class="bg-background text-base-content flex h-screen min-h-fit w-full flex-col">
				<div class="bg-background h-1/6 min-h-fit p-4">Background<br /></div>
				<div class="bg-base-100 h-1/6 min-h-fit w-5/6 p-4">base-100<br /></div>
				<div class="bg-base-150 h-1/6 min-h-fit w-4/6 p-4">base-150<br /></div>
				<div class="bg-base-200 h-1/6 min-h-fit w-3/6 p-4">base-200<br /></div>
				<div class="bg-base-250 h-1/6 min-h-fit w-2/6 p-4">base-250<br /></div>
				<div class="bg-base-300 h-1/6 min-h-fit w-1/6 p-4">base-300<br /></div>
			</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Text and colors for content">
		<BackgroundRows><ContentText /></BackgroundRows>
		<p class="body-small text-outline-variant">The dividers are outline-variant.</p>
	</AccordionItem>
	<AccordionItem title="Text and colors for app functionality">
		<BackgroundRows><AppText /></BackgroundRows>
		<p class="body-small text-outline-variant">The dividers are outline-variant.</p>
	</AccordionItem>
	<AccordionItem title="Interactions for content control">
		<BackgroundRows><ContentInteraction /></BackgroundRows>
		<p class="body-small text-outline-variant">The dividers are outline-variant.</p>
	</AccordionItem>
	<AccordionItem title="Interactions for app functionality">
		<BackgroundRows><AppInteraction /></BackgroundRows>
		<p class="body-small text-outline-variant">The dividers are outline-variant.</p>
	</AccordionItem>
	<AccordionItem title="Containers">
		<BackgroundRows><Containers /></BackgroundRows>
		<p class="body-small text-outline-variant">The dividers are outline-variant.</p>
		<p class="body-small text-outline">Borders of boxes outline.</p>
	</AccordionItem>
</div>
