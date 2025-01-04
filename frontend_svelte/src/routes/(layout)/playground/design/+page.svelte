<script lang="ts">
	import Card from '$components/Card.svelte';
	import Heading from '$components/Heading.svelte';
	import AccordionItem from './AccordionItem.svelte';
	import ContentText from './ContentText.svelte';
	import AppText from './AppText.svelte';
</script>

<Heading>🚧 Construction sites for design experiments 🚧</Heading>

<div class="grid grid-cols-1 gap-8 md:grid-cols-3">
	<Card
		title="FlyonUI 1"
		description="Playground and showcase for flyonUI components and design"
		href={`/playground/design/flyonui`}
	></Card>
	<Card
		title="Material Design 3"
		description="Playground and showcase for Material Design 3 components and design"
		href={`/playground/design/materialdesign`}
	></Card>
	<Card
		title="TailwindCSS 3"
		description="Formating playground for styling with TailwindCSS utility classes"
		href={`/playground/design/tailwindcss`}
	></Card>
	<Card
		title="Comparison"
		description="Directly putting components right next to each other to compare them"
		href={`/playground/design/comparison`}
	></Card>
</div>

<Heading>👍 Results, ready for use 👍</Heading>

<div class="accordion accordion-bordered divide-y" data-accordion-always-open="">
	<AccordionItem title="Backgrounds">
		<div class="bg-background h-screen w-full text-base-content grid grid-cols-5">
			<div class="bg-background p-4 text-center">Background</div>
			<div class="bg-base-100 min-h-fit h-2/5 p-4 text-center">base-100</div>
			<div class="bg-base-150 min-h-fit h-3/5 p-4 text-center">base-150</div>
			<div class="bg-base-200 min-h-fit h-4/5 p-4  text-center">base-200</div>
			<div class="bg-base-300 min-h-fit h-5/5 p-4 text-center">base-300</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Text and colors for content">
		<div class="bg-background h-screen w-full text-base-content grid grid-cols-5">
			<div class="p-4">
				Background
				<ContentText />
			</div>
			<div class="bg-base-100 min-h-fit h-2/5 p-4">
				base-100
				<ContentText />
			</div>
			<div class="bg-base-150 min-h-fit h-3/5 p-4">
				base-150
				<ContentText />
			</div>
			<div class="bg-base-200 min-h-fit h-4/5 p-4">
				base-200
				<ContentText />
			</div>
			<div class="bg-base-300 min-h-fit h-5/5 p-4">
				base-300
				<ContentText />
			</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Text and colors for app functionality">
		<div class="bg-background h-screen w-full text-base-content grid grid-cols-5">
			<div class="p-4">
				Background
				<AppText />
			</div>
			<div class="bg-base-100 min-h-fit h-2/5 p-4">
			base-100
				<AppText />
			</div>
			<div class="bg-base-150 min-h-fit h-3/5 p-4">
				base-150
				<AppText />
			</div>
			<div class="bg-base-200 min-h-fit h-4/5 p-4">
				base-200
				<AppText />
			</div>
			<div class="bg-base-300 min-h-fit h-5/5 p-4">
				base-300
				<AppText />
			</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Colors">
		<div class="bg-base-100 skeleton h-screen w-full text-base-content">
			<div class="flex flex-col gap-2 p-4">
				<p class="body-small">Base-100 background with base-content text</p>
				<div class="flex flex-row flex-wrap gap-4 pl-6">
					<div class="flex flex-col gap-2">
						<!-- <p class="text-primary body-small">Primary text on base-100 background</p> -->
						<button class="btn btn-primary rounded-full bg-primary text-primary-content"
							>Primary</button
						>
						<button class="btn-primary-container btn rounded-full">Primary Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-secondary rounded-full bg-secondary text-secondary-content"
							>Secondary</button
						>
						<button class="btn-secondary-container btn rounded-full">Secondary Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-accent rounded-full bg-accent text-accent-content">Accent</button
						>
						<button class="btn-accent-container btn rounded-full">Accent Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn-neutral btn rounded-full bg-neutral text-neutral-content"
							>Neutral</button
						>
						<button class="btn-neutral-container btn rounded-full">Neutral Container</button>
					</div>
				</div>
				<div class="flex flex-row flex-wrap gap-4 pl-6">
					<div class="flex flex-col gap-2">
						<button class="btn btn-info rounded-full bg-info text-info-content">Info</button>
						<button class="btn-info-container btn rounded-full">Info Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-success rounded-full bg-success text-success-content"
							>Success</button
						>
						<button class="btn-success-container btn rounded-full">Success Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-warning rounded-full bg-warning text-warning-content"
							>Warning</button
						>
						<button class="btn-warning-container btn rounded-full">Warning Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-error rounded-full bg-error text-error-content">Error</button>
						<button class="btn-error-container btn rounded-full">Error Container</button>
					</div>
				</div>
			</div>
		</div>
	</AccordionItem>
</div>
