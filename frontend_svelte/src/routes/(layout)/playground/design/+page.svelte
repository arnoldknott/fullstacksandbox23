<script lang="ts">
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

<div class="accordion accordion-bordered bg-base-150" data-accordion-always-open="">
	<AccordionItem title="Backgrounds and Surfaces">
		<ColorTile background="--md-sys-color-background" color="--md-sys-color-on-background" />
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
